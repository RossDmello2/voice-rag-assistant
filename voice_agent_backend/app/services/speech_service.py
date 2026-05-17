"""
SpeechService — Kokoro TTS (GPU) + Groq STT.

- Kokoro-82M runs on CUDA (lazy-loaded, ~165MB VRAM)
- Groq Whisper for STT (primary), faster-whisper (fallback)
- Docker sidecar HTTP fallback for TTS
"""

import io
import re
import json
import struct
import logging
import asyncio
import unicodedata
from typing import AsyncGenerator, Optional

try:
    import numpy as np
except ImportError:
    np = None
import httpx
from num2words import num2words

from app.core.config import settings
from app.core.onnx_runtime import configure_onnxruntime_gpu_environment
from app.services.http_client import get_http_client

logger = logging.getLogger(__name__)


class SpeechService:
    """Singleton-friendly speech service. Instantiate once at module level."""

    def __init__(self):
        self._kokoro_pipeline = None
        self._kokoro_loaded = False
        self._faster_whisper_model = None
        self._current_hardware = "cpu"
        self._available_voices = []
        self._backchannel_cache = {}  # {phrase: base64_pcm}

    async def precompute_backchannels(self, voice: Optional[str] = None):
        """
        Pre-synthesize backchannel phrases at startup for zero-latency dispatch.
        Stored as Base64 encoded Int16 PCM strings.
        """
        import base64
        phrases = getattr(settings, "BACKCHANNEL_PHRASES", ["mhm", "yeah", "I see", "got it", "right"])
        v = voice or getattr(settings, "TTS_VOICE", "af_heart")
        hw = getattr(settings, "TTS_HARDWARE", "gpu")
        
        logger.info(f"Pre-computing {len(phrases)} backchannels for voice {v}...")
        
        for phrase in phrases:
            try:
                pcm_bytes = b""
                async for chunk in self.synthesize_stream(phrase, voice=v, hardware=hw):
                    pcm_bytes += chunk
                
                if pcm_bytes:
                    b64 = base64.b64encode(pcm_bytes).decode("ascii")
                    self._backchannel_cache[phrase] = b64
                    logger.info(f"Cached backchannel: '{phrase}'")
            except Exception as e:
                logger.error(f"Failed to pre-compute backchannel '{phrase}': {e}")

    def get_backchannel(self, phrase: Optional[str] = None) -> Optional[str]:
        """Fetch a pre-computed backchannel chunk from cache."""
        if not self._backchannel_cache:
            return None
        if phrase and phrase in self._backchannel_cache:
            return self._backchannel_cache[phrase]
        
        # Pick random if no specific phrase requested
        import random
        return random.choice(list(self._backchannel_cache.values()))

    def _normalize_tts_text(self, text: str) -> str:
        """Normalize model output into Kokoro-friendlier plain text."""
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", text)
        replacements = {
            "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " ",
        }
        for src, dest in replacements.items():
            text = text.replace(src, dest)

        # 1. Currency: "$1,000.50" -> "one thousand dollars and fifty cents"
        # We use a pattern that captures the $ and the number with possible commas/decimals
        def replace_currency(match):
            raw_val = match.group(1).replace(',', '')
            try:
                # num2words currency mode handles decimal conversion to 'cents' elegantly
                return num2words(float(raw_val), to='currency', currency='USD')
            except:
                return f"{raw_val} dollars"
        
        text = re.sub(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b', replace_currency, text)

        # 2. Ordinals: "1st" -> "first", "22nd" -> "twenty-second"
        def replace_ordinals(match):
            val = match.group(1)
            try:
                return num2words(int(val), to='ordinal')
            except:
                return match.group(0)
        
        text = re.sub(r'\b(\d+)(?:st|nd|rd|th)\b', replace_ordinals, text, flags=re.IGNORECASE)

        # 3. Numeric ranges: "5-7" -> "5 to 7"
        text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\g<1> to \g<2>', text)

        # 4. Percent: "10%" -> "10 percent"
        text = re.sub(r'(\d+(?:\.\d+)?)%', r'\g<1> percent', text)

        # 5. PROTECTED PATTERNS (Don't word-normalize phone numbers)
        # We find tokens that look like words (no numbers) and tokens that ARE numbers.
        # We only run num2words on 'lonely' numbers or small sequences.
        def replace_numbers(match):
            num_str = match.group(1).replace(',', '')
            # If it's more than 4 digits and has no context, Kokoro might fail.
            # But if it's 10 digits, it's a phone number, keep it as digits.
            if len(num_str) >= 7 and len(num_str) <= 15:
                return " ".join(num_str) # Spaced out for digit-by-digit
            try:
                if len(num_str) > 0:
                    return num2words(int(num_str))
            except:
                pass
            return num_str

        # Only convert integers of 1-6 digits (Values, not IDs/Phones)
        text = re.sub(r'\b(\d{1,6})\b', replace_numbers, text)

        # 6. Emails: "user@domain.com" -> "user at domain dot com"
        text = re.sub(r'(\S+)@(\S+)\.(\S+)', r'\g<1> at \g<2> dot \g<3>', text)
        
        # 7. Common Shorthand/Phonetics
        text = re.sub(r'\s+&\s+', ' and ', text)
        
        # Convert non-vocalic backchannels into Kokoro-friendly phonetic equivalents
        text = re.sub(r'\b[Mm]hm\b', 'mm-hmm', text)
        text = re.sub(r'\b[Uu]hm\b', 'um', text)

        # Clean extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text


    # ── Kokoro TTS ──────────────────────────────────────────────────

    def _get_kokoro_pipeline(self, hardware: Optional[str] = None):
        """
        Lazy-load Kokoro ONNX model and Misaki phonemizer.
        Automatically handles hardware selection (CPU/GPU).
        """
        if hardware is None:
            hardware = getattr(settings, "TTS_HARDWARE", "gpu")
            
        # Re-initialize if hardware preference changed
        if self._kokoro_loaded and self._current_hardware == hardware:
            return self._kokoro_pipeline

        try:
            configure_onnxruntime_gpu_environment()

            model_path = getattr(settings, "KOKORO_MODEL_PATH", "data/models/kokoro-v1.0.onnx")
            voices_path = getattr(settings, "KOKORO_VOICES_PATH", "data/models/voices-v1.0.bin")
            
            import os
            if not os.path.exists(model_path):
                logger.error(f"Kokoro model not found at {model_path}")
                self._kokoro_loaded = True
                return None
            
            from kokoro_onnx import Kokoro
            from misaki import en
            import onnxruntime as ort

            # Try loading CUDA/cuDNN/MSVC runtime DLLs before provider discovery.
            try:
                ort.preload_dlls(cuda=True, cudnn=True, msvc=True)
            except Exception as preload_err:
                logger.warning(f"ONNX Runtime DLL preload failed: {preload_err}")
            
            # Record current hardware preference
            self._current_hardware = hardware
            
            # Rely on ONNX Runtime auto-selection (confirmed detection of CUDA)
            logger.info(f"Initializing Kokoro (Hardware preference: {hardware})")
            
            sess_options = ort.SessionOptions()
            if hardware.lower() == "gpu":
                # Nitro 5 Optimization: Match i5-11400H total threads
                sess_options.intra_op_num_threads = settings.ONNX_INTRA_OP_THREADS
                sess_options.inter_op_num_threads = settings.ONNX_INTER_OP_THREADS
                sess_options.enable_mem_pattern = True
                sess_options.enable_cpu_mem_arena = True
                
                # Force CUDA with cuDNN optimizations
                providers = [
                    ("CUDAExecutionProvider", {
                        "device_id": 0,
                        "arena_extend_strategy": "kSameAsRequested",
                        "gpu_mem_limit": 3 * 1024 * 1024 * 1024, # Reserve 3GB for Kokoro/Embed
                        "cudnn_conv_algo_search": "DEFAULT",
                        "do_copy_in_default_stream": True,
                    }),
                    "CPUExecutionProvider"
                ]
            else:
                providers = ["CPUExecutionProvider"]

            # Use Kokoro.from_session to apply hardware-specific session options
            session = ort.InferenceSession(model_path, sess_options=sess_options, providers=providers)
            self._kokoro_pipeline = Kokoro.from_session(session, voices_path)

            self._g2p = en.G2P()
            self._kokoro_loaded = True
            
            # Pre-load available voices list
            self.get_available_voices()
            
            logger.info(f"Kokoro-ONNX and Misaki G2P loaded successfully with {hardware} hardware.")
            return self._kokoro_pipeline

        except ImportError as e:
            logger.warning(f"Kokoro-ONNX or Misaki not installed: {e}. TTS will use fallback.")
            self._kokoro_loaded = True
            return None
        except Exception as e:
            logger.error(f"Failed to load Kokoro-ONNX: {e}", exc_info=True)
            self._kokoro_loaded = True
            return None

    def get_available_voices(self) -> list:
        """Read and return list of voice keys from the voices bin file."""
        if self._available_voices:
            return self._available_voices
            
        try:
            voices_path = getattr(settings, "KOKORO_VOICES_PATH", "data/models/voices-v1.0.bin")
            import os
            if os.path.exists(voices_path):
                data = np.load(voices_path, allow_pickle=False)
                self._available_voices = sorted(list(data.files))
                return self._available_voices
        except Exception as e:
            logger.error(f"Error loading voice list: {e}")
            
        return ["af_heart"] # Fallback


    def _synthesize_native_chunks(self, text: str, voice: str = "af_heart", speed: float = 1.0, hardware: Optional[str] = None):
        """
        Synchronous generator yielding int16 PCM bytes from Kokoro-ONNX.
        """
        text = self._normalize_tts_text(text)
        if not text:
            return

        kokoro = self._get_kokoro_pipeline(hardware=hardware)
        if kokoro is None:
            return

        available_voices = self.get_available_voices()
        if available_voices and voice not in available_voices:
            logger.warning(f"Requested unknown voice '{voice}', falling back to af_heart.")
            voice = "af_heart"

        # Use Misaki G2P for phonemization (as in the repo)
        phonemes, _ = self._g2p(text)
        
        # The caller (generate_response_node) already sends text in sentence chunks.
        # Primary normalization into plain speech text.
        text = self._normalize_tts_text(text)
        if not text:
            return

        try:
            samples, sample_rate = kokoro.create(
                text,
                voice=voice,
                speed=speed,
                lang="en-us"
            )
            if samples is not None:
                # samples is a numpy float32 array
                audio_int16 = (np.asarray(samples, dtype=np.float32) * 32767).astype(np.int16)
                yield audio_int16.tobytes()
        except Exception as e:
            logger.warning(f"Kokoro failed on text chunk '{text[:80]}': {e}")

    async def synthesize_stream(self, text: str, voice: str = "af_heart", speed: float = 1.0, hardware: Optional[str] = None) -> AsyncGenerator[bytes, None]:
        """
        Async generator yielding int16 PCM chunks at 24kHz.
        Tries Kokoro native first, falls back to Docker sidecar.
        """
        kokoro_mode = getattr(settings, "KOKORO_MODE", "native")

        if kokoro_mode == "native":
            try:
                # Resolve hardware preference (defaults to GPU if available)
                hw = hardware or getattr(settings, "TTS_HARDWARE", "gpu")
                
                loop = asyncio.get_running_loop()
                sync_gen = self._synthesize_native_chunks(text, voice=voice, speed=speed, hardware=hw)


                queue: asyncio.Queue = asyncio.Queue()
                exhausted = object()

                def _fill_queue():
                    # B-03 FIX: runs in thread, pushes chunks as Kokoro produces them
                    try:
                        for chunk in sync_gen:
                            loop.call_soon_threadsafe(queue.put_nowait, chunk)
                    except Exception as e:
                        loop.call_soon_threadsafe(queue.put_nowait, ("__error__", e))
                    finally:
                        loop.call_soon_threadsafe(queue.put_nowait, exhausted)

                # B-03 FIX: do NOT await — start thread concurrently with drain loop
                fill_future = loop.run_in_executor(None, _fill_queue)

                try:
                    while True:
                        item = await queue.get()
                        if item is exhausted:
                            break
                        if isinstance(item, tuple) and len(item) == 2 and item[0] == "__error__":
                            raise item[1]
                        yield item
                finally:
                    await fill_future  # ensure thread joined cleanly

                return
            except Exception as e:
                logger.warning(f"Kokoro native TTS failed (mode={kokoro_mode}): {e}")
                # Retry once on CPU for stability before falling through.
                if hw.lower() == "gpu":
                    try:
                        logger.info("Retrying Kokoro native TTS on CPU fallback.")
                        async for chunk in self.synthesize_stream(text, voice=voice, speed=speed, hardware="cpu"):
                            yield chunk
                        return
                    except Exception as cpu_err:
                        logger.warning(f"CPU fallback after GPU TTS failure also failed: {cpu_err}")
                # Fall through to Docker fallback

        # Docker fallback (also used when native mode fails)
        docker_url = getattr(settings, "KOKORO_DOCKER_URL", "http://localhost:8880")
        if docker_url:
            try:
                async for chunk in self._synthesize_docker(text, voice=voice, speed=speed):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"Docker TTS failed: {e}")

        # Silent Fallback (Ensures frontend never hangs)
        logger.warning("All TTS engines failed or unavailable. Emitting silent fallback to prevent frontend hang.")
        # Yield 0.5 seconds of silence (24000 Hz * 0.5s * 2 bytes/sample)
        silent_chunk = b'\x00' * 24000
        yield silent_chunk


    async def _synthesize_docker(self, text: str, voice: str = "af_heart", speed: float = 1.0) -> AsyncGenerator[bytes, None]:
        """Stream TTS audio from Docker sidecar."""
        docker_url = getattr(settings, "KOKORO_DOCKER_URL", "http://localhost:8880")
        url = f"{docker_url}/tts"

        payload = {"text": text, "voice": voice, "speed": speed}

        client = await get_http_client()
        async with client.stream("POST", url, json=payload, timeout=30.0) as resp:
            if resp.status_code != 200:
                raise RuntimeError(f"Docker TTS returned {resp.status_code}")
            async for chunk in resp.aiter_bytes(chunk_size=8192):
                yield chunk

    # ── STT (Speech-to-Text) ────────────────────────────────────────

    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio using Groq Whisper API (primary).
        Falls back to faster-whisper (local) on failure.
        """
        # Try Groq Whisper first
        try:
            return await self._transcribe_groq(audio_data, language)
        except Exception as e:
            logger.warning(f"Groq STT failed: {e}. Trying local fallback.")

        # Local fallback with faster-whisper
        try:
            return await self._transcribe_local(audio_data, language)
        except Exception as e:
            logger.error(f"Local STT also failed: {e}")
            return ""

    async def _transcribe_groq(self, audio_data: bytes, language: str = "en") -> str:
        """Transcribe using Groq Whisper API."""
        groq_api_key = settings.GROQ_API_KEY
        groq_base = settings.GROQ_BASE

        url = f"{groq_base}/audio/transcriptions"

        headers = {
            "Authorization": f"Bearer {groq_api_key}",
        }

        files = {
            "file": ("audio.webm", audio_data, "audio/webm"),
        }
        data = {
            "model": "whisper-large-v3",
            "language": language,
            "response_format": "json",
        }

        client = await get_http_client()
        resp = await client.post(url, headers=headers, files=files, data=data, timeout=30.0)
        resp.raise_for_status()
        result = resp.json()
        return result.get("text", "").strip()

    async def _transcribe_local(self, audio_data: bytes, language: str = "en") -> str:
        """Transcribe using local faster-whisper model."""
        if self._faster_whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                self._faster_whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            except ImportError:
                raise RuntimeError("faster-whisper not installed")

        import tempfile
        import os

        # Write audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_data)
            tmp_path = f.name

        try:
            loop = asyncio.get_running_loop()
            segments, info = await loop.run_in_executor(
                None,
                lambda: self._faster_whisper_model.transcribe(tmp_path, language=language)
            )
            text = " ".join(seg.text for seg in segments).strip()
            return text
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


# ── Singleton ──────────────────────────────────────────────────────
speech_service = SpeechService()
