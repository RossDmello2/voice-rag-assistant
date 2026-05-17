import os
import logging
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_kokoro():
    print("\n" + "="*50)
    print("VERIFYING KOKORO-ONNX INITIALIZATION")
    print("="*50)
    
    model_path = getattr(settings, "KOKORO_MODEL_PATH", "data/models/kokoro-v1.0.onnx")
    voices_path = getattr(settings, "KOKORO_VOICES_PATH", "data/models/voices-v1.0.bin")
    
    print(f"Model path: {model_path} (Exists: {os.path.exists(model_path)})")
    print(f"Voices path: {voices_path} (Exists: {os.path.exists(voices_path)})")
    
    if os.path.exists(model_path):
         print(f"Model size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
    
    try:
        from kokoro_onnx import Kokoro
        from misaki import en
        
        print("Imported kokoro_onnx and misaki.")
        
        # Test basic phonemizer
        g2p = en.G2P()
        phonemes, _ = g2p("Hello")
        print(f"Phonemization test successful (length: {len(phonemes)})")
        
        # Try to init Kokoro (will likely fail if voices.bin is 15 bytes)
        print("Attempting to initialize Kokoro class...")
        try:
            kokoro = Kokoro(model_path, voices_path)
            print("SUCCESS: Kokoro initialized!")
        except Exception as e:
            print(f"KOKORO INIT FAILED: {e}")
            if "voices.bin" in str(e) or "voices" in str(e).lower():
                print("Suggestion: Your voices.bin file might be invalid or for a different model version.")

        
    except ImportError as e:
        print(f"FAILED: Imports failed: {e}")
    except Exception as e:
        print(f"FAILED: Initialization failed: {e}")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    verify_kokoro()
