/* ══════════════════════════════════════════════════════════════
   VOICE AGENT — Thin Frontend Script
   Backend: FastAPI at same origin
   ══════════════════════════════════════════════════════════════ */

// ═══════════════════════════════════════════════════════════════
//  SECTION 1: CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const CONFIG = {
    BACKEND_BASE: '',    // empty = same origin (FastAPI serves frontend)
    COLLECTION: 'agent_knowledge',
    MEMORY_PAIRS: 10,
    ENABLE_VOICE_PIPELINE: true,
    PREFER_BACKEND_TTS: true,

    STT_ENGINE: 'browser',
    STT_LANGUAGE: 'en',
    SILENCE_TIMEOUT_MS: 1000,
    MAX_RECORDING_MS: 30000,
    MIN_AUDIO_SIZE_BYTES: 1000,

    TTS_RATE: 1.3,
    TTS_PITCH: 1.0,
    TTS_VOICE: 'af_heart',
    TTS_HARDWARE: 'gpu',


    RENDER_THROTTLE_MS: 12, // Optimized for 144Hz display
    BOOT_RETRY_DELAY_MS: 3000,
    TTS_INTER_SENTENCE_PAUSE_MS: 100,

    ENABLE_BACKCHANNEL: false,
    ENABLE_VAD_INTERRUPTION: false,
    ENABLE_HAPTIC_FEEDBACK: true,
    ENABLE_TRANSLATION: false,

    STORAGE_PREFIX: 'ssa_',

    PREPROCESS_ENABLED: true,
    EXPAND_ABBREVIATIONS: true,
    NUMBERS_TO_WORDS: true,
    ADD_PAUSES: true,

    RESET_LEGACY_LOCAL_STATE_VERSION: 2,
    RETRIEVAL_CONFIDENCE_FLOOR: 0.05,
    SUMMARY_CONFIDENCE_FLOOR: 0.03,
};

// ═══════════════════════════════════════════════════════════════
//  AUTH MODULE — JWT token storage + same-origin fetch interceptor
// ═══════════════════════════════════════════════════════════════




var LANGUAGE_META = {
    'en': { name: 'English',    sttBcp47: 'en-US', ttsLang: 'en-US', whisperCode: 'en' },
    'es': { name: 'Spanish',    sttBcp47: 'es-ES', ttsLang: 'es-ES', whisperCode: 'es' },
    'fr': { name: 'French',     sttBcp47: 'fr-FR', ttsLang: 'fr-FR', whisperCode: 'fr' },
    'de': { name: 'German',     sttBcp47: 'de-DE', ttsLang: 'de-DE', whisperCode: 'de' },
    'it': { name: 'Italian',    sttBcp47: 'it-IT', ttsLang: 'it-IT', whisperCode: 'it' },
    'pt': { name: 'Portuguese', sttBcp47: 'pt-BR', ttsLang: 'pt-BR', whisperCode: 'pt' },
    'zh': { name: 'Chinese',    sttBcp47: 'zh-CN', ttsLang: 'zh-CN', whisperCode: 'zh' },
    'ja': { name: 'Japanese',   sttBcp47: 'ja-JP', ttsLang: 'ja-JP', whisperCode: 'ja' },
    'ar': { name: 'Arabic',     sttBcp47: 'ar-SA', ttsLang: 'ar-SA', whisperCode: 'ar' },
    'hi': { name: 'Hindi',      sttBcp47: 'hi-IN', ttsLang: 'hi-IN', whisperCode: 'hi' },
    'ru': { name: 'Russian',    sttBcp47: 'ru-RU', ttsLang: 'ru-RU', whisperCode: 'ru' },
    'ko': { name: 'Korean',     sttBcp47: 'ko-KR', ttsLang: 'ko-KR', whisperCode: 'ko' },
    'tr': { name: 'Turkish',    sttBcp47: 'tr-TR', ttsLang: 'tr-TR', whisperCode: 'tr' },
    'nl': { name: 'Dutch',      sttBcp47: 'nl-NL', ttsLang: 'nl-NL', whisperCode: 'nl' },
    'pl': { name: 'Polish',     sttBcp47: 'pl-PL', ttsLang: 'pl-PL', whisperCode: 'pl' },
    'sv': { name: 'Swedish',    sttBcp47: 'sv-SE', ttsLang: 'sv-SE', whisperCode: 'sv' },
    'id': { name: 'Indonesian', sttBcp47: 'id-ID', ttsLang: 'id-ID', whisperCode: 'id' },
};

function isBrowserSTT() { return CONFIG.STT_ENGINE === 'browser'; }
function getActiveLanguageMeta() { return LANGUAGE_META[STATE.translation.activeLanguage] || LANGUAGE_META['en']; }
function isNonEnglishMode() { return CONFIG.ENABLE_TRANSLATION && STATE.translation.activeLanguage !== 'en'; }
function getOrCreateSessionId() {
    if (!STATE.conversation.currentSessionId) STATE.conversation.currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).slice(2,8);
    return STATE.conversation.currentSessionId;
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 2: STATE
// ═══════════════════════════════════════════════════════════════

const STATE = {
    services: {
        ollama: { online: false, models: [] },
        qdrant: { online: false, collectionReady: false },
        groq: { online: false },
    },
    allReady: false,
    phase: 'idle',
    activeCollection: '',
    lastIntentWasDocument: false,
    lastRetrieval: { query: '', rawQuery: '', resolvedQuery: '', chunks: [], sources: [], pages: [], sourceDetails: [], contextText: '', mode: '', answer: '', lastUserMessage: '', intentMode: '', resultCount: 0, topScore: 0, retryCount: 0 },
    stt: { recognition: null, mediaStream: null, mediaRecorder: null, audioChunks: [], isRecording: false, silenceTimer: null, maxTimer: null, audioContext: null, analyser: null, mimeType: '', listenerState: 'idle', predictiveTriggered: false, backchannelTimer: null, predictiveTimer: null, lastTranscript: '' },
    tts: { isSpeaking: false, isPaused: false, currentUtterance: null, nativeVoices: [], speakReject: null, currentVolume: 1, activeBoundaryCharIndex: 0, activeDisplayText: '', hasReceivedFirstToken: false },
    conversation: { history: [], turnCount: 0, sessions: [], currentSessionId: null },
    memory: { committedMessages: [], committedRetrieval: null, inProgressTurn: null, activeTurnId: 0, sttSessionId: 0, isInterrupting: false },
    documents: { ingested: [], isIngesting: false },
    llm: { isGenerating: false, abortController: null, currentResponse: '', hasReceivedFirstToken: false, activeChatModel: '', activeChatProvider: '' },
    embeddings: { activeModel: '', activeProvider: '' },
    performance: { embeddingCache: [] },
    ui: { handsFreeModeActive: false, settingsPanelOpen: false, documentsPanelOpen: false, historyPanelOpen: false, currentTranscript: '', activeAgentMsgId: null, speakId: 0 },
    pronunciations: {},
    vad: { instance: null, isLoaded: false, isEnabled: false, isArmed: false, lastPhaseChange: 0, lastSpeechStart: 0, lastInterrupt: 0, timer: null, phaseMode: '', monitorStream: null, monitorContext: null, monitorSource: null, analyser: null, sampleTimer: null, rawSpeechActive: false, rawSpeechEndedAt: 0, lastEnergyAt: 0, baselineEnergy: 0.008, currentEnergy: 0, thresholdMultiplier: 1, graceUntil: 0, cooldownUntil: 0, disabledByFailure: false, candidate: { isActive: false, startedAt: 0, confirmationStartedAt: 0, confirmationExpiresAt: 0, loweredTts: false, confirmed: false }, captureMode: '', context: { turnId: 0, spokenText: '', unspokenText: '', fullResponse: '', lastAssistantHistoryIndex: -1, pendingPromptInjection: '', resumeEligible: false, captureInFlight: false } },
    voiceSafety: { watchdogTimer: null, micDisabledAt: 0 },
    feedback: { responseLengthPreference: 'normal', lastCorrectionAt: 0, lastRepeatRequestAt: 0, lastEarlyInterruptionAt: 0 },
    backchannel: { isPlaying: false, cooldownUntil: 0, currentUtterance: null, hasPlayedThisTurn: false, timers: { processingDelay: null, retrievalDelay: null }, waiters: [], startedAt: 0, text: '' },
    ttsStream: { buffer: '', sentenceQueue: [], isActive: false, currentTurnId: 0, hasSpokenFirstSentence: false, enqueuedCharCount: 0, streamComplete: false, pendingFinalText: '', pendingResponseMeta: null, pendingSources: null, completionHandled: false, isDraining: false, drainTimer: null, lastSpokenSentence: '', fullTextPushed: 0 },
    guardrails: { lastInputFlag: '', lastOutputFlag: '', lastRetrievalFlag: '' },
    translation: { activeLanguage: 'en', lastInputLanguage: 'en', isTranslating: false, lastOriginalInput: '', lastTranslatedInput: '', lastOriginalResponse: '', lastTranslatedResponse: '' },
    network: { activeControllers: [] },
    orb: { animFrame: null, audioLevel: 0, tick: 0 },
};


// ═══════════════════════════════════════════════════════════════
//  SECTION 16: VOICE PIPELINE — LangGraph + Kokoro TTS + Interrupts
// ═══════════════════════════════════════════════════════════════

// ── 16a: Trigger words for voice pipeline ──
var VOICE_TRIGGER_WORDS = [
    'hey assistant', 'ok assistant', 'okay assistant',
    'hey bot', 'hello assistant', 'hi assistant',
    'computer', 'jarvis'
];

function containsTriggerWord(text) {
    if (!text) return false;
    var lower = text.toLowerCase().trim();
    for (var i = 0; i < VOICE_TRIGGER_WORDS.length; i++) {
        if (lower.indexOf(VOICE_TRIGGER_WORDS[i]) === 0 || lower === VOICE_TRIGGER_WORDS[i]) {
            return true;
        }
    }
    return false;
}

function stripTriggerWord(text) {
    if (!text) return text;
    var lower = text.toLowerCase();
    for (var i = 0; i < VOICE_TRIGGER_WORDS.length; i++) {
        if (lower.indexOf(VOICE_TRIGGER_WORDS[i]) === 0) {
            return text.substring(VOICE_TRIGGER_WORDS[i].length).trim();
        }
    }
    return text;
}

// ── 16b: PCM Audio Playback (Kokoro TTS output) ──
var PCMAudioPlayer = {
    audioContext: null,
    sourceNode: null,
    gainNode: null,
    isPlaying: false,
    queue: [],
    sampleRate: 24000,
    nextStartTime: 0,

    init: function () {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: this.sampleRate });
            this.gainNode = this.audioContext.createGain();
            this.gainNode.connect(this.audioContext.destination);
        } catch (e) {
            console.error('PCM AudioPlayer init failed:', e);
        }
    },

    enqueuePCMChunk: function (base64PCM) {
        if (!this.audioContext) this.init();
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume().catch(function () { });
        }
        try {
            var binaryStr = atob(base64PCM);
            var bytes = new Uint8Array(binaryStr.length);
            for (var i = 0; i < binaryStr.length; i++) bytes[i] = binaryStr.charCodeAt(i);
            var int16 = new Int16Array(bytes.buffer);
            var float32 = new Float32Array(int16.length);
            for (var j = 0; j < int16.length; j++) float32[j] = int16[j] / 32768.0;
            this.queue.push(float32);
            if (!this.isPlaying) this.drainQueue();
        } catch (e) {
            console.error('PCM chunk decode error:', e);
        }
    },

    drainQueue: function () {
        if (this.queue.length === 0) { this.isPlaying = false; return; }
        this.isPlaying = true;
        var pcmData = this.queue.shift();
        var buffer = this.audioContext.createBuffer(1, pcmData.length, this.sampleRate);
        buffer.getChannelData(0).set(pcmData);
        var source = this.audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(this.gainNode);
        var now = this.audioContext.currentTime;
        
        // Adaptive buffering: if queue is low (< 2 chunks), slightly increase 
        // the lookahead window (start delay) to absorb network jitter.
        var baseDelay = 0.01; 
        if (this.queue.length < 2) baseDelay = 0.05; 

        if (!this.nextStartTime || this.nextStartTime < now) {
            this.nextStartTime = now + baseDelay;
        }
        source.start(this.nextStartTime);
        this.nextStartTime += buffer.duration;
        var self = this;
        source.onended = function () {
            if (self.queue.length === 0 && self.nextStartTime <= self.audioContext.currentTime + 0.05) {
                self.isPlaying = false;
                self.nextStartTime = 0;
                return;
            }
            self.drainQueue();
        };
        this.sourceNode = source;
    },

    setVolume: function (level) {
        if (this.gainNode) {
            this.gainNode.gain.setTargetAtTime(level, this.audioContext.currentTime, 0.1);
        }
    },

    stop: function () {
        this.queue = [];
        this.isPlaying = false;
        this.nextStartTime = 0;
        if (this.sourceNode) { try { this.sourceNode.stop(); } catch (e) { } this.sourceNode = null; }
    }
};

// ── 16c: Progress Bar for Graph Stages ──
var STAGE_ORDER = [
    'translate_input', 'check_interrupt', 'classify_intent',
    'retrieve_context', 'check_confidence', 'ultrathinking',
    'generate_response', 'synthesize_speech', 'update_context'
];

var STAGE_DISPLAY = {
    'translate_input': 'Translating...',
    'check_interrupt': 'Checking...',
    'classify_intent': 'Classifying intent...',
    'retrieve_context': 'Searching documents...',
    'check_confidence': 'Evaluating confidence...',
    'ultrathinking': 'Deep Thinking (ULTRATHINK)...',
    'generate_response': 'Generating response...',
    'synthesize_speech': 'Synthesizing speech...',
    'update_context': 'Updating context...'
};

function updatePipelineProgress(stageName) {
    var bar = document.getElementById('pipeline-progress-bar');
    var label = document.getElementById('pipeline-stage-label');
    var idx = STAGE_ORDER.indexOf(stageName);
    if (idx === -1) return;
    var pct = Math.round(((idx + 1) / STAGE_ORDER.length) * 100);
    if (bar) bar.style.width = pct + '%';
    if (label) label.textContent = STAGE_DISPLAY[stageName] || stageName;
}

function showPipelineProgress() {
    var container = document.getElementById('pipeline-progress-container');
    if (container) container.classList.remove('hidden');
    var bar = document.getElementById('pipeline-progress-bar');
    if (bar) bar.style.width = '0%';
}

function hidePipelineProgress() {
    var container = document.getElementById('pipeline-progress-container');
    if (container) container.classList.add('hidden');
}

// ── 16d: Voice Pipeline SSE Handler ──
var VoicePipeline = {
    activeThreadId: null,
    isActive: false,

    send: function (message, options) {
        if (typeof VoicePipeline === 'undefined') { console.error('VoicePipeline NOT INITIALIZED'); return; }
        options = options || {};
        var receivedAudio = false;
        var threadId = options.threadId || ('voice_' + Date.now());
        this.activeThreadId = threadId;
        this.isActive = true;

        var body = {
            session_id: getOrCreateSessionId(),
            message: message,
            thread_id: threadId,
            language: STATE.translation.activeLanguage || 'en',
            collection: getActiveCollection(),
            has_documents: !!(STATE.documents && STATE.documents.ingested && STATE.documents.ingested.length),
            last_intent_was_document: STATE.lastIntentWasDocument,
        };
        if (STATE.llm.activeChatModel) body.chat_model = STATE.llm.activeChatModel;
        if (STATE.llm.activeChatProvider) body.chat_provider = STATE.llm.activeChatProvider;
        if (STATE.embeddings.activeModel) body.embed_model = STATE.embeddings.activeModel;
        
        // Pass TTS preferences
        body.tts_voice = CONFIG.TTS_VOICE;
        body.tts_speed = CONFIG.TTS_RATE;
        body.hardware = CONFIG.TTS_HARDWARE;


        showPipelineProgress();
        setPhase('processing');

        var controller = new AbortController();
        STATE.llm.abortController = controller;
        STATE.llm.isGenerating = true;
        STATE.llm.hasReceivedFirstToken = false;
        STATE.llm.currentResponse = '';

        var turnId = STATE.memory.inProgressTurn && STATE.memory.inProgressTurn.id ? STATE.memory.inProgressTurn.id : (++STATE.memory.activeTurnId);
        if (!STATE.memory.inProgressTurn) STATE.memory.inProgressTurn = { id: turnId, userText: message, source: options.source || 'text', startTime: Date.now() };
        resetStreamingTtsState(turnId);
        resetBackchannelForTurn();

        var agentMsgId = createAgentMessage();

        fetch('/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            signal: controller.signal
        }).then(function (response) {
            if (!response.ok) throw new Error(response.status === 401 ? 'auth_required' : ('Stream error ' + response.status));
            var reader = response.body.getReader();
            var decoder = new TextDecoder();
            var buffer = '';

            function processChunk() {
                return reader.read().then(function (result) {
                    if (result.done) {
                        if (!receivedAudio) {
                            STATE.ttsStream.pendingFinalText = STATE.llm.currentResponse || '';
                            STATE.ttsStream.pendingResponseMeta = { isDocumentResponse: true, queryInfo: {}, skipBackendTts: true };
                            flushRemainingTtsBuffer(turnId);
                        } else if (!CONFIG.PREFER_BACKEND_TTS) {
                            flushRemainingTtsBuffer(turnId);
                        }
                        hidePipelineProgress();
                        VoicePipeline.isActive = false;
                        STATE.llm.isGenerating = false;
                        commitInProgressTurn(turnId);
                        safeSetIdleAfterTurn(turnId);
                        return;
                    }
                    buffer += decoder.decode(result.value, { stream: true });
                    var lines = buffer.split('\n');
                    buffer = lines.pop() || '';

                    for (var i = 0; i < lines.length; i++) {
                        var line = lines[i].trim();
                        if (!line.startsWith('data: ')) continue;
                        var payload = line.substring(6);
                        if (payload === '[DONE]') {
                            if (!receivedAudio) {
                                STATE.ttsStream.pendingFinalText = STATE.llm.currentResponse || '';
                                STATE.ttsStream.pendingResponseMeta = { isDocumentResponse: true, queryInfo: {}, skipBackendTts: true };
                                flushRemainingTtsBuffer(turnId);
                            } else if (!CONFIG.PREFER_BACKEND_TTS) {
                                flushRemainingTtsBuffer(turnId);
                            }
                            commitInProgressTurn(turnId);
                            STATE.memory.committedMessages.push({ role: 'user', content: message });
                            STATE.memory.committedMessages.push({ role: 'assistant', content: stripInlineSourceCitations(STATE.llm.currentResponse || '') });
                            while (STATE.memory.committedMessages.length > CONFIG.MEMORY_PAIRS * 2) STATE.memory.committedMessages.shift();
                            syncCommittedMemory();
                            hidePipelineProgress();
                            VoicePipeline.isActive = false;
                            STATE.llm.isGenerating = false;
                            safeSetIdleAfterTurn(turnId);
                            if (STATE.ui.handsFreeModeActive && STATE.phase === 'idle') setTimeout(startListening, 400);
                            return;
                        }
                        try {
                            var data = JSON.parse(payload);
                            // Token — same SSE contract as /chat
                            if (data.token) {
                                if (!STATE.llm.hasReceivedFirstToken) STATE.llm.hasReceivedFirstToken = true;
                                STATE.llm.currentResponse += data.token;
                                if (!CONFIG.PREFER_BACKEND_TTS) pushStreamTokenToTtsBuffer(data.token, turnId);
                                var safeHtml = renderMarkdownSafe(STATE.llm.currentResponse);
                                updateAgentMessage(agentMsgId, safeHtml, false);
                            }
                            // Stage — progress UI
                            if (data.stage) {
                                updatePipelineProgress(data.stage);
                                // Play backchannel on retrieval stage
                                if (data.stage === 'retrieve_context') {
                                    scheduleProcessingBackchannel(message, turnId);
                                }
                                if (data.stage === 'ultrathinking') {
                                    setPhase('ultrathinking');
                                }
                            }
                            // Audio chunk — PCM from Kokoro TTS
                            if (data.audio) {
                                receivedAudio = true;
                                setPhase('speaking');
                                PCMAudioPlayer.enqueuePCMChunk(data.audio);
                            }
                            // Audio done signal
                            if (data.audio_done) {
                                // PCM playback will finish on its own
                            }
                            // Translated response
                            if (data.translated) {
                                STATE.translation.lastTranslatedResponse = data.translated;
                                updateAgentMessage(agentMsgId, renderMarkdownSafe(data.translated), false);
                            }
                            // Sources
                            if (data.sources) {
                                appendSourcesTag(agentMsgId, data.sources);
                            }
                        } catch (e) {
                            // Skip malformed JSON
                        }
                    }
                    return processChunk();
                });
            }
            return processChunk();
        }).catch(function (err) {
            if (err.name === 'AbortError') return;
            console.error('Voice pipeline error:', err);
            if (isAuthError(err)) {
                AUTH.clear();
                showAuthModal();
                setAuthError('Please sign in to continue.');
                hidePipelineProgress();
                VoicePipeline.isActive = false;
                STATE.llm.isGenerating = false;
                setPhase('idle');
                return;
            }
            toast('Pipeline error: ' + err.message, 'error');
            hidePipelineProgress();
            VoicePipeline.isActive = false;
            STATE.llm.isGenerating = false;
            setPhase('idle');
        });
    },

    interrupt: function (newQuery) {
        if (!this.activeThreadId) return;
        if (!newQuery) {
            return;
        }
        var body = { new_query: newQuery || '' };
        fetch('/chat/interrupt/' + this.activeThreadId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        }).then(function (r) {
            if (!r.ok) throw new Error('Interrupt failed ' + r.status);
            return r.text();
        }).then(function () {
            console.log('Interrupt acknowledged');
        }).catch(function (err) {
            console.error('Interrupt error:', err);
        });
    }
};

window.voicePipelineSubmit = function (text, source) {
    if (!CONFIG.ENABLE_VOICE_PIPELINE) return false;
    if (typeof VoicePipeline === 'undefined') return false; 
    if (source === 'voice' && typeof containsTriggerWord === 'function' && containsTriggerWord(text)) {
        var cleaned = stripTriggerWord(text);
        if (cleaned) {
            VoicePipeline.send(cleaned);
            return true;
        }
    }
    if (CONFIG.PREFER_BACKEND_TTS) {
        VoicePipeline.send(text);
        return true;
    }
    return false;
};

// ── 16f: Pipeline progress bar DOM injection (runs on DOMContentLoaded) ──
document.addEventListener('DOMContentLoaded', function () {
    var existing = document.getElementById('pipeline-progress-container');
    if (!existing) {
        var container = document.createElement('div');
        container.id = 'pipeline-progress-container';
        container.className = 'pipeline-progress-container hidden';
        container.innerHTML = '<div class="pipeline-progress-track"><div id="pipeline-progress-bar" class="pipeline-progress-bar"></div></div><span id="pipeline-stage-label" class="pipeline-stage-label"></span>';
        var controlBar = document.getElementById('control-bar');
        if (controlBar) controlBar.parentNode.insertBefore(container, controlBar.nextSibling);
    }
});


// ═══════════════════════════════════════════════════════════════

//  SECTION 3: DOM CACHE
// ═══════════════════════════════════════════════════════════════

const DOM = {};

function cacheDom() {
    DOM.orbCanvas = document.getElementById('orb-canvas');
    DOM.phaseLabel = document.getElementById('phase-label');
    DOM.transcriptArea = document.getElementById('transcript-area');
    DOM.messageList = document.getElementById('message-list');
    DOM.inputArea = document.getElementById('input-area');
    DOM.controlBar = document.getElementById('control-bar');
    DOM.textInput = document.getElementById('text-input');
    DOM.sendBtn = document.getElementById('send-btn');
    DOM.micBtn = document.getElementById('mic-btn');
    DOM.stopBtn = document.getElementById('stop-btn');
    DOM.uploadBtn = document.getElementById('upload-btn');
    DOM.docsBtn = document.getElementById('docs-btn');
    DOM.fileInput = document.getElementById('file-input');
    DOM.handsfreeToggle = document.getElementById('handsfree-toggle');
    DOM.settingsBtn = document.getElementById('settings-btn');
    DOM.settingsPanel = document.getElementById('settings-panel');
    DOM.settingsOverlay = document.getElementById('settings-overlay');
    DOM.settingsClose = document.getElementById('settings-close');
    DOM.historyBtn = document.getElementById('history-btn');
    DOM.historyPanel = document.getElementById('history-panel');
    DOM.historyOverlay = document.getElementById('history-overlay');
    DOM.historyClose = document.getElementById('history-close');
    DOM.historyList = document.getElementById('history-list');
    DOM.documentsPanel = document.getElementById('documents-panel');
    DOM.documentsOverlay = document.getElementById('documents-overlay');
    DOM.documentsClose = document.getElementById('documents-close');
    DOM.documentList = document.getElementById('document-list');
    DOM.dropZone = document.getElementById('drop-zone');
    DOM.ingestionProgress = document.getElementById('ingestion-progress');
    DOM.progressBar = document.getElementById('progress-bar');
    DOM.progressText = document.getElementById('progress-text');
    DOM.toastContainer = document.getElementById('toast-container');
    DOM.ttsVoiceSelect = document.getElementById('tts-voice-select');
    DOM.ttsHardwareSelect = document.getElementById('tts-hardware-select');
    DOM.ttsVoiceSearch = document.getElementById('native-voice-search');
    DOM.nativeVoiceGroup = document.getElementById('native-voice-group');

    DOM.ttsRateSlider = document.getElementById('tts-rate-slider');
    DOM.ttsRateValue = document.getElementById('tts-rate-value');
    DOM.ttsPitchSlider = document.getElementById('tts-pitch-slider');
    DOM.ttsPitchValue = document.getElementById('tts-pitch-value');
    DOM.sttEngineSelect = document.getElementById('stt-engine-select');
    DOM.sttLanguageSelect = document.getElementById('stt-language-select');
    DOM.silenceTimeoutSlider = document.getElementById('silence-timeout-slider');
    DOM.silenceTimeoutValue = document.getElementById('silence-timeout-value');
    DOM.groqKeyInput = document.getElementById('groq-key-input');
    DOM.groqKeyToggle = document.getElementById('groq-key-toggle');
    DOM.chatModelSelect = document.getElementById('chat-model-select');
    DOM.embedModelSelect = document.getElementById('embed-model-select');
    DOM.collectionSelect = document.getElementById('collection-select');
    DOM.settingsCollectionSelect = document.getElementById('settings-collection-select');
    DOM.newCollectionRow = document.getElementById('new-collection-row');
    DOM.newCollectionInput = document.getElementById('new-collection-input');
    DOM.newCollectionConfirm = document.getElementById('new-collection-confirm');
    DOM.newCollectionCancel = document.getElementById('new-collection-cancel');
    DOM.pronunciationList = document.getElementById('pronunciation-list');
    DOM.pronWordInput = document.getElementById('pron-word-input');
    DOM.pronReplacementInput = document.getElementById('pron-replacement-input');
    DOM.pronAddBtn = document.getElementById('pron-add-btn');
    DOM.newChatBtn = document.getElementById('new-chat-btn');
    DOM.clearKnowledgeBtn = document.getElementById('clear-knowledge-btn');
    DOM.languageIndicator = document.getElementById('status-language');
    DOM.activeLanguageLabel = document.getElementById('active-language-label');
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 4: UTILITIES
// ═══════════════════════════════════════════════════════════════

let messageCounter = 0;

function uuid() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (Math.random() * 16) | 0;
        return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    });
}

function escapeHtml(text) { var d = document.createElement('div'); d.textContent = text; return d.innerHTML; }

function timedFetch(url, options, timeoutMs) {
    options = options || {};
    timeoutMs = timeoutMs || 30000;
    var controller = new AbortController();
    STATE.network.activeControllers.push(controller);
    var timer = setTimeout(function () { controller.abort(); }, timeoutMs);
    var merged = Object.assign({}, options, { signal: controller.signal });
    return fetch(url, merged).then(function (resp) {
        clearTimeout(timer);
        var idx = STATE.network.activeControllers.indexOf(controller);
        if (idx !== -1) STATE.network.activeControllers.splice(idx, 1);
        return resp;
    }).catch(function (err) {
        clearTimeout(timer);
        var idx = STATE.network.activeControllers.indexOf(controller);
        if (idx !== -1) STATE.network.activeControllers.splice(idx, 1);
        if (err.name === 'AbortError') throw new Error('Request timed out');
        throw err;
    });
}

function saveToStorage(key, value) { try { localStorage.setItem(CONFIG.STORAGE_PREFIX + key, JSON.stringify(value)); } catch (e) { console.warn('Storage write failed:', e); } }
function loadFromStorage(key, defaultValue) { try { var raw = localStorage.getItem(CONFIG.STORAGE_PREFIX + key); return raw ? JSON.parse(raw) : defaultValue; } catch (e) { return defaultValue; } }
function removeFromStorage(key) { try { localStorage.removeItem(CONFIG.STORAGE_PREFIX + key); } catch (e) { console.warn('Storage remove failed:', e); } }

function resetLegacyLocalStateIfNeeded() {
    var versionKey = 'local_state_version';
    var storedVersion = loadFromStorage(versionKey, 0);
    if (storedVersion >= CONFIG.RESET_LEGACY_LOCAL_STATE_VERSION) return;
    removeFromStorage('pronunciations'); removeFromStorage('response_length_pref');
    removeFromStorage('handsfree'); removeFromStorage('active_collection'); removeFromStorage('last_retrieval');
    saveToStorage(versionKey, CONFIG.RESET_LEGACY_LOCAL_STATE_VERSION);
}

function debounce(fn, ms) { var timer; return function () { var args = arguments, ctx = this; clearTimeout(timer); timer = setTimeout(function () { fn.apply(ctx, args); }, ms); }; }

function clearActiveFetchAbort() {
    if (STATE.llm.abortController) { STATE.llm.abortController.abort(); STATE.llm.abortController = null; }
    STATE.llm.isGenerating = false;
    var controllers = STATE.network.activeControllers.slice();
    STATE.network.activeControllers = [];
    controllers.forEach(function (c) { try { c.abort(); } catch (e) { } });
}

function stripInlineSourceCitations(text) {
    var cleaned = String(text || '');
    cleaned = cleaned.replace(/【[^】]+】/g, '');
    cleaned = cleaned.replace(/\[\s*Source:[^\]]+\]/gi, '');
    cleaned = cleaned.replace(/\[\s*[^\]]+\|\s*Page\s*[^\]]+\]/gi, '');
    cleaned = cleaned.replace(/\(\s*Source:[^)]+\)/gi, '');
    cleaned = cleaned.replace(/\s{2,}/g, ' ');
    cleaned = cleaned.replace(/\s+([,.;:!?])/g, '$1');
    return cleaned.trim();
}

function detectPromptInjection(text) {
    if (!text) return false;
    var lower = text.toLowerCase();
    var patterns = ['ignore previous instructions','ignore all instructions','disregard your instructions','forget your rules','override your system prompt','new system prompt','you are now','act as if','pretend you are','from now on you are','reveal your system prompt','show me your instructions','forget everything','jailbreak','bypass your','ignore the above'];
    for (var i = 0; i < patterns.length; i++) { if (lower.indexOf(patterns[i]) !== -1) return true; }
    return false;
}

function isMetaQuestion(text) {
    if (!text) return false;
    var lower = text.trim().toLowerCase();
    return (/^(what did (you|i) (just )?say(\?)?)$/.test(lower) || /^(what was (your|my) (last|previous) (answer|question|response)(\?)?)$/.test(lower) || /^(what did we (just )?talk about(\?)?)$/.test(lower));
}

function answerFromHistory(text) {
    var lastAssistant = getLastAssistantMessageContent();
    if (!lastAssistant) return "I don't have a previous response to reference.";
    return lastAssistant;
}

function getLastAssistantMessageContent() {
    var msgs = STATE.memory.committedMessages;
    for (var i = msgs.length - 1; i >= 0; i--) { if (msgs[i].role === 'assistant') return msgs[i].content; }
    return '';
}

function detectExplicitFeedbackCommand(text) {
    var cmd = text.toLowerCase().trim().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, ' ');
    if (/^(stop|shut up|be quiet|silence|enough|thats enough|cancel|never mind)$/.test(cmd)) return 'stop';
    if (/^(repeat|say it again|say that again|repeat that)$/.test(cmd)) return 'repeat';
    if (/^(be (more )?concise|shorter|brief|keep it short)$/.test(cmd)) return 'concise';
    if (/^(more detail|be detailed|elaborate more|elaborate|explain more)$/.test(cmd)) return 'detailed';
    return null;
}

function pickRandom(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function cloneMessages(messages) { return JSON.parse(JSON.stringify(messages || [])); }
function createEmptyLastRetrieval() { return { query: '', rawQuery: '', resolvedQuery: '', chunks: [], sources: [], pages: [], sourceDetails: [], contextText: '', mode: '', answer: '', lastUserMessage: '', intentMode: '', resultCount: 0, topScore: 0, retryCount: 0 }; }
function cloneRetrieval(retrieval) { return Object.assign(createEmptyLastRetrieval(), retrieval || {}); }

// ── Local storage helpers for per-collection data ──
function documentsKey(col) { return 'docs_' + col; }
function conversationKey(col) { return 'conv_' + col; }
function retrievalKey(col) { return 'retr_' + col; }
function sessionsKey(col) { return 'sess_' + col; }
function sessionIdKey(col) { return 'sid_' + col; }

function saveDocumentsForCollection(col, docs) { saveToStorage(documentsKey(col), docs); }
function loadDocumentsForCollection(col) { return loadFromStorage(documentsKey(col), []); }
function saveConversationForCollection(col, history) { saveToStorage(conversationKey(col), history); }
function loadConversationForCollection(col) { return loadFromStorage(conversationKey(col), []); }
function saveRetrievalForCollection(col, retrieval) { saveToStorage(retrievalKey(col), retrieval); }
function loadRetrievalForCollection(col) { return loadFromStorage(retrievalKey(col), null); }
function saveSessionsForCollection(col, sessions) { saveToStorage(sessionsKey(col), sessions); }
function loadSessionsForCollection(col) { return loadFromStorage(sessionsKey(col), []); }
function saveSessionIdForCollection(col, id) { saveToStorage(sessionIdKey(col), id); }
function ensureCollectionSessionId(col) { var id = loadFromStorage(sessionIdKey(col), null); if (!id) { id = 'session_' + Date.now(); saveSessionIdForCollection(col, id); } return id; }

function getActiveCollection() { return STATE.activeCollection || CONFIG.COLLECTION; }
function initializeCommittedMemory() { STATE.memory.committedMessages = cloneMessages(STATE.conversation.history); STATE.memory.committedRetrieval = cloneRetrieval(STATE.lastRetrieval); }
function syncCommittedMemory() { STATE.conversation.history = cloneMessages(STATE.memory.committedMessages); STATE.conversation.turnCount = STATE.conversation.history.length; persistActiveCollectionConversation(); }
function persistActiveCollectionConversation() { saveConversationForCollection(getActiveCollection(), STATE.conversation.history); }
function persistActiveCollectionRetrieval() { saveRetrievalForCollection(getActiveCollection(), STATE.lastRetrieval); }
function resetLastRetrievalState() { STATE.lastRetrieval = createEmptyLastRetrieval(); }

function renderConversationToUi() {
    if (!DOM.messageList) return;
    DOM.messageList.innerHTML = '';
    STATE.memory.committedMessages.forEach(function (m) { addMessage(m.role, m.content); });
}

// ── VAD helpers ──
function resetVadCandidateState() { STATE.vad.candidate = { isActive: false, startedAt: 0, confirmationStartedAt: 0, confirmationExpiresAt: 0, loweredTts: false, confirmed: false }; }
function restoreTtsVolume() { STATE.tts.currentVolume = 1; }
function lowerTtsVolumeForConfirmation() { STATE.tts.currentVolume = 0.3; }


// ═══════════════════════════════════════════════════════════════
//  SECTION 4b: BACKCHANNEL SYSTEM
// ═══════════════════════════════════════════════════════════════

var BACKCHANNEL_PHRASES = ['Hmm let me think','Let me look into that','One sec','Give me a moment','Let me think about that','Yeah give me a moment','Hmm okay','Sure hold on'];
var BACKCHANNEL_RETRIEVAL_PHRASES = ['Let me think about that','One moment','Let me see','Hmm let me figure that out','Give me a sec','Let me look into that'];
var BACKCHANNEL_NUMBER_PHRASES = ['Hmm let me see', 'One moment', 'Let me check those figures'];
var BACKCHANNEL_PERSON_PHRASES = ['Let me think', 'Hmm okay', 'Let me find that name'];

var NO_INFO_PROMPTS = ["Hmm I don't really know about that","I'm not sure I share that knowledge","I don't think I possess that information","That's not something I'm currently aware of"];
var PRE_ANSWER_PHRASES = ['Alright so','Okay so','Yeah so','Right so','Got it','Sure so'];
var PRE_ANSWER_DOCUMENT_PHRASES = ['Okay so','Alright so','Right','Yeah so'];
var PRE_ANSWER_NUMBER_PHRASES = ['Okay so','Right so','Alright'];
var PRE_ANSWER_PERSON_PHRASES = ['Okay so','Right','Yeah so'];

var TURN_TAKING_SUFFIXES = ['What else can I help with?','Is there anything else?','Anything else on your mind?'];
var IMPLICIT_ACKNOWLEDGE = ['Sure thing.','On it.','Got it.','Absolutely.','Of course.','Certainly.'];

var BACKCHANNEL_LAST_PHRASE = '';
var PRE_ANSWER_LAST_PHRASE = '';

function cancelBackchannelTimers() { if (STATE.backchannel.timers.processingDelay) { clearTimeout(STATE.backchannel.timers.processingDelay); STATE.backchannel.timers.processingDelay = null; } if (STATE.backchannel.timers.retrievalDelay) { clearTimeout(STATE.backchannel.timers.retrievalDelay); STATE.backchannel.timers.retrievalDelay = null; } }

function cancelActiveBackchannel() {
    var hadActiveBackchannel = !!STATE.backchannel.currentUtterance;
    if (STATE.backchannel.currentUtterance && NativeTTS.synth) { try { NativeTTS.synth.cancel(); } catch (e) { } }
    if (hadActiveBackchannel) finishBackchannelPlayback();
    else { STATE.backchannel.currentUtterance = null; STATE.backchannel.isPlaying = false; STATE.backchannel.startedAt = 0; STATE.backchannel.text = ''; }
}

function finishBackchannelPlayback() {
    STATE.backchannel.isPlaying = false; STATE.backchannel.currentUtterance = null; STATE.backchannel.startedAt = 0; STATE.backchannel.text = '';
    var waiters = STATE.backchannel.waiters || []; STATE.backchannel.waiters = [];
    while (waiters.length) { try { waiters.shift()(); } catch (e) { } }
    if (STATE.ttsStream && STATE.ttsStream.sentenceQueue && STATE.ttsStream.sentenceQueue.length > 0) { scheduleStreamingSentenceDrain(STATE.memory.activeTurnId, 0); }
}

function resetBackchannelForTurn() { cancelBackchannelTimers(); cancelActiveBackchannel(); STATE.backchannel.hasPlayedThisTurn = false; STATE.backchannel.cooldownUntil = 0; STATE.backchannel.waiters = []; }

function selectBackchannelPhrase(isRetrieval, queryText) {
    var phrases = isRetrieval ? BACKCHANNEL_RETRIEVAL_PHRASES : BACKCHANNEL_PHRASES;
    var lower = String(queryText || '').toLowerCase();
    if (lower) {
        if (/\b(number|amount|total|count|how many|percentage|price)\b/.test(lower)) {
            phrases = BACKCHANNEL_NUMBER_PHRASES;
        } else if (/\b(who|manager|director|name)\b/.test(lower)) {
            phrases = BACKCHANNEL_PERSON_PHRASES;
        }
    }
    if (!phrases.length) return 'Let me check that';
    var idx = Math.floor(Math.random() * phrases.length);
    var phrase = phrases[idx];
    if (phrases.length > 1 && phrase === BACKCHANNEL_LAST_PHRASE) phrase = phrases[(idx + 1) % phrases.length];
    BACKCHANNEL_LAST_PHRASE = phrase;
    return phrase;
}

function selectPreAnswerPhrase(queryText, responseMeta) {
    var lower = String(queryText || '').toLowerCase();
    var phrases = PRE_ANSWER_PHRASES;
    if (responseMeta && responseMeta.isDocumentResponse) {
        phrases = PRE_ANSWER_DOCUMENT_PHRASES;
    }
    if (/\b(number|amount|total|count|how many|percentage|price)\b/.test(lower)) {
        phrases = PRE_ANSWER_NUMBER_PHRASES;
    } else if (/\b(who|manager|director|name)\b/.test(lower)) {
        phrases = PRE_ANSWER_PERSON_PHRASES;
    }
    if (!phrases.length) phrases = PRE_ANSWER_PHRASES;
    var idx = Math.floor(Math.random() * phrases.length);
    var phrase = phrases[idx];
    if (phrases.length > 1 && phrase === PRE_ANSWER_LAST_PHRASE) phrase = phrases[(idx + 1) % phrases.length];
    PRE_ANSWER_LAST_PHRASE = phrase;
    return phrase;
}

function buildSpokenAnswerText(text, options) {
    options = options || {};
    var cleaned = stripInlineSourceCitations(text);
    if (!cleaned) return cleaned;
    if (isNonEnglishMode()) return cleaned;
    if (!options.turnId || options.skipAcknowledgement) return cleaned;
    if (STATE.backchannel.hasPlayedThisTurn) return cleaned;
    var isAction = false;
    var qLower = (options.queryText || '').toLowerCase();
    if (options.responseMeta && !options.responseMeta.isDocumentResponse) { if (/^(tell|show|give|explain|describe|help|find)\b/.test(qLower)) isAction = true; }
    if (isAction) return pickRandom(IMPLICIT_ACKNOWLEDGE) + ' ' + cleaned;
    var prefix = selectPreAnswerPhrase(options.queryText || '', options.responseMeta || null);
    return prefix ? (prefix + '. ' + cleaned) : cleaned;
}

function playBackchannelPhrase(isRetrieval, turnId, queryText) {
    if (!CONFIG.ENABLE_BACKCHANNEL || STATE.backchannel.hasPlayedThisTurn || STATE.backchannel.isPlaying) return;
    if (Date.now() < STATE.backchannel.cooldownUntil || turnId !== STATE.memory.activeTurnId || STATE.phase !== 'processing' || !NativeTTS.synth) return;
    var phrase = selectBackchannelPhrase(isRetrieval, queryText);
    STATE.backchannel.isPlaying = true; STATE.backchannel.hasPlayedThisTurn = true; STATE.backchannel.startedAt = Date.now(); STATE.backchannel.text = phrase;
    var utt = new SpeechSynthesisUtterance(phrase);
    utt.rate = 1.04; utt.volume = 0.58;
    if (CONFIG.TTS_VOICE && STATE.tts.nativeVoices.length) { var found = STATE.tts.nativeVoices.find(function (v) { return v.name === CONFIG.TTS_VOICE; }); if (found) utt.voice = found; }
    STATE.backchannel.currentUtterance = utt;
    utt.onend = function () { finishBackchannelPlayback(); STATE.backchannel.cooldownUntil = Date.now() + 500; };
    utt.onerror = function () { finishBackchannelPlayback(); };
    NativeTTS.synth.speak(utt);
}

function scheduleProcessingBackchannel(queryText, turnId) {
    if (!CONFIG.ENABLE_BACKCHANNEL) return;
    cancelBackchannelTimers();
    STATE.backchannel.timers.processingDelay = setTimeout(function () {
        if (turnId !== STATE.memory.activeTurnId || STATE.phase !== 'processing' || STATE.llm.hasReceivedFirstToken) return;
        playBackchannelPhrase(false, turnId, queryText);
    }, 350);
}

function waitForBackchannelToFinish(maxWaitMs) {
    maxWaitMs = typeof maxWaitMs === 'number' ? maxWaitMs : 1200;
    return new Promise(function (resolve) {
        if (!STATE.backchannel.isPlaying || !STATE.backchannel.currentUtterance) { resolve(); return; }
        STATE.backchannel.waiters.push(resolve);
        setTimeout(function () { var waiters = STATE.backchannel.waiters || []; var idx = waiters.indexOf(resolve); if (idx === -1) return; waiters.splice(idx, 1); cancelActiveBackchannel(); resolve(); }, maxWaitMs);
    });
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 4c: STREAMING TTS SYSTEM
// ═══════════════════════════════════════════════════════════════

function resetStreamingTtsState(turnId) {
    if (STATE.ttsStream.drainTimer) { clearTimeout(STATE.ttsStream.drainTimer); STATE.ttsStream.drainTimer = null; }
    STATE.ttsStream.buffer = ''; STATE.ttsStream.sentenceQueue = []; STATE.ttsStream.isActive = false;
    STATE.ttsStream.currentTurnId = turnId || 0; STATE.ttsStream.hasSpokenFirstSentence = false;
    STATE.ttsStream.enqueuedCharCount = 0; STATE.ttsStream.streamComplete = false;
    STATE.ttsStream.pendingFinalText = ''; STATE.ttsStream.pendingResponseMeta = null;
    STATE.ttsStream.pendingSources = null; STATE.ttsStream.completionHandled = false;
    STATE.ttsStream.isDraining = false; STATE.ttsStream.lastSpokenSentence = ''; STATE.ttsStream.fullTextPushed = 0;
}

function cancelStreamingTts() {
    if (STATE.ttsStream.drainTimer) { clearTimeout(STATE.ttsStream.drainTimer); STATE.ttsStream.drainTimer = null; }
    STATE.ttsStream.isActive = false; STATE.ttsStream.isDraining = false; STATE.ttsStream.sentenceQueue = [];
    STATE.ttsStream.streamComplete = true; STATE.ttsStream.completionHandled = true;
    STATE.ttsStream.buffer = ''; STATE.ttsStream.lastSpokenSentence = '';
    TTSManager.stop();
}

function normalizeStreamingSentenceSpacing(text) {
    return String(text || '').replace(/\r\n/g, '\n').replace(/\s*\n\s*/g, ' ').replace(/[ \t]+/g, ' ').replace(/\s+([,.;:!?])/g, '$1').trim();
}

function isSpeakableStreamingFragment(text) {
    var value = normalizeStreamingSentenceSpacing(text);
    if (!value) return false;
    if (/^[\s.,!?;:|*`~\-–—()[\]{}\\/]+$/.test(value)) return false;
    if (/^(?:[-*•]+|\d+[.)])$/.test(value)) return false;
    var alnum = value.replace(/[^A-Za-z0-9]/g, '');
    if (!alnum) return false;
    if (alnum.length <= 1 && !/^[AIai]$/.test(alnum)) return false;
    return true;
}

function extractCompletedSentencesFromBuffer(buffer, flushAll) {
    if (!buffer) return { sentences: [], remainder: '' };
    var source = String(buffer).replace(/\r\n/g, '\n');
    var sentences = [];
    var boundaryPattern = /([.!?]+(?:["'""')\]]+)?)(?=\s+|$)|\n+/g;
    var lastConsumedIndex = 0;
    var match;
    function pushCandidate(fragment) { var cleaned = normalizeStreamingSentenceSpacing(fragment); if (!isSpeakableStreamingFragment(cleaned)) return; sentences.push(cleaned); }
    while ((match = boundaryPattern.exec(source)) !== null) {
        var boundaryEnd = boundaryPattern.lastIndex;
        var chunk = source.slice(lastConsumedIndex, boundaryEnd);
        var boundaryToken = match[0] || '';
        var isNewlineBoundary = boundaryToken.indexOf('\n') !== -1;
        var hasSentencePunctuation = !isNewlineBoundary;
        var nextChar = source.charAt(boundaryEnd);
        if (!flushAll && hasSentencePunctuation && nextChar && !/\s/.test(nextChar)) continue;
        pushCandidate(chunk);
        lastConsumedIndex = boundaryEnd;
    }
    if (flushAll) { pushCandidate(source.slice(lastConsumedIndex)); lastConsumedIndex = source.length; }
    return { sentences: sentences, remainder: source.slice(lastConsumedIndex) };
}

function scheduleStreamingSentenceDrain(turnId, delayMs) {
    if (turnId !== STATE.ttsStream.currentTurnId) return;
    if (STATE.ttsStream.drainTimer) clearTimeout(STATE.ttsStream.drainTimer);
    STATE.ttsStream.drainTimer = setTimeout(function () { STATE.ttsStream.drainTimer = null; drainStreamingSentenceQueue(turnId); }, typeof delayMs === 'number' ? delayMs : 0);
}

function completeStreamingTurnIfReady(turnId) {
    if (STATE.ttsStream.completionHandled || !STATE.ttsStream.streamComplete) return;
    if (STATE.ttsStream.sentenceQueue.length > 0 || STATE.tts.isSpeaking) return;
    if (turnId !== STATE.memory.activeTurnId) return;
    STATE.ttsStream.completionHandled = true;
    var meta = STATE.ttsStream.pendingResponseMeta;
    var finalText = STATE.ttsStream.pendingFinalText;
    if (meta && meta.isDocumentResponse) {
        STATE.lastRetrieval.answer = finalText;
        STATE.lastIntentWasDocument = true;
        STATE.memory.committedRetrieval = cloneRetrieval(STATE.lastRetrieval);
        persistActiveCollectionRetrieval();
    }
    commitInProgressTurn(turnId);
    safeSetIdleAfterTurn(turnId);
    if (STATE.ui.handsFreeModeActive && STATE.phase === 'idle') setTimeout(startListening, 400);
}

function drainStreamingSentenceQueue(turnId) {
    if (turnId !== STATE.ttsStream.currentTurnId || turnId !== STATE.memory.activeTurnId || STATE.memory.isInterrupting) return;
    if (STATE.ttsStream.isDraining || STATE.tts.isSpeaking) return;
    if (STATE.backchannel.isPlaying) { scheduleStreamingSentenceDrain(turnId, 100); return; }
    if (STATE.ttsStream.sentenceQueue.length === 0) { completeStreamingTurnIfReady(turnId); return; }
    var sentence = STATE.ttsStream.sentenceQueue.shift();
    if (!isSpeakableStreamingFragment(sentence)) { scheduleStreamingSentenceDrain(turnId, 0); return; }
    STATE.ttsStream.isDraining = true;
    var speakable = TextPreprocessor.preprocess(sentence, { exactWording: true });
    speakable = normalizeStreamingSentenceSpacing(speakable);
    if (!isSpeakableStreamingFragment(speakable)) { STATE.ttsStream.isDraining = false; scheduleStreamingSentenceDrain(turnId, 0); return; }
    if (!STATE.ttsStream.hasSpokenFirstSentence) { STATE.ttsStream.hasSpokenFirstSentence = true; setPhase('speaking'); }
    STATE.ttsStream.isActive = true; STATE.ttsStream.lastSpokenSentence = speakable;
    TTSManager.speak(speakable, { rate: CONFIG.TTS_RATE, pitch: CONFIG.TTS_PITCH, voice: CONFIG.TTS_VOICE, turnId: turnId, alreadySegmented: true }).then(function () {
        STATE.ttsStream.isDraining = false;
        if (turnId !== STATE.memory.activeTurnId || STATE.memory.isInterrupting) return;
        scheduleStreamingSentenceDrain(turnId, CONFIG.TTS_INTER_SENTENCE_PAUSE_MS);
    }).catch(function () {
        STATE.ttsStream.isDraining = false;
        if (turnId !== STATE.memory.activeTurnId || STATE.memory.isInterrupting) return;
        scheduleStreamingSentenceDrain(turnId, CONFIG.TTS_INTER_SENTENCE_PAUSE_MS);
    });
}

function enqueueStreamingSentence(sentence, turnId) {
    if (!isSpeakableStreamingFragment(sentence) || turnId !== STATE.ttsStream.currentTurnId || turnId !== STATE.memory.activeTurnId) return;
    STATE.ttsStream.sentenceQueue.push(normalizeStreamingSentenceSpacing(sentence));
    if (!STATE.tts.isSpeaking && !STATE.ttsStream.isDraining && !STATE.backchannel.isPlaying) scheduleStreamingSentenceDrain(turnId, 0);
}

function pushStreamTokenToTtsBuffer(token, turnId) {
    if (turnId !== STATE.memory.activeTurnId || turnId !== STATE.ttsStream.currentTurnId || typeof token !== 'string' || !token) return;
    STATE.ttsStream.buffer += token;
    var extracted = extractCompletedSentencesFromBuffer(STATE.ttsStream.buffer, false);
    STATE.ttsStream.buffer = extracted.remainder;
    extracted.sentences.forEach(function (s) { enqueueStreamingSentence(s, turnId); });
}

function flushRemainingTtsBuffer(turnId) {
    if (turnId !== STATE.ttsStream.currentTurnId) return;
    var extracted = extractCompletedSentencesFromBuffer(STATE.ttsStream.buffer, true);
    STATE.ttsStream.buffer = '';
    extracted.sentences.forEach(function (s) { enqueueStreamingSentence(s, turnId); });
    STATE.ttsStream.streamComplete = true;
    completeStreamingTurnIfReady(turnId);
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 4d: VAD INTERRUPTION SYSTEM
// ═══════════════════════════════════════════════════════════════

function disarmInterruptionDetection(reason) {
    if (!STATE.vad.isArmed) return;
    STATE.vad.isArmed = false; STATE.vad.phaseMode = '';
    resetVadCandidateState(); restoreTtsVolume();
    if (STATE.vad.sampleTimer) { clearInterval(STATE.vad.sampleTimer); STATE.vad.sampleTimer = null; }
}

function armInterruptionDetectionForPhase(phase) {
    if (!STATE.vad.isEnabled || STATE.vad.disabledByFailure) return;
    if (phase !== 'processing' && phase !== 'speaking') return;
    STATE.vad.isArmed = true; STATE.vad.phaseMode = phase;
    STATE.vad.graceUntil = Date.now() + (phase === 'speaking' ? 500 : 300);
    resetVadCandidateState();
    startVadEnergySampler();
}

function sampleCurrentAudioEnergy() {
    var analyser = STATE.vad.analyser;
    if (!analyser) return 0;
    var buf = new Float32Array(analyser.fftSize);
    analyser.getFloatTimeDomainData(buf);
    var sum = 0;
    for (var i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
    return Math.sqrt(sum / buf.length);
}

function updateVadBaseline(energy) { STATE.vad.baselineEnergy = STATE.vad.baselineEnergy * 0.95 + energy * 0.05; }

function computeDynamicInterruptionThreshold(phase) {
    var base = STATE.vad.baselineEnergy;
    var mult = phase === 'speaking' ? 3.5 : 2.5;
    return Math.max(base * mult * STATE.vad.thresholdMultiplier, 0.012);
}

function startInterruptionCandidate(now) { STATE.vad.candidate.isActive = true; STATE.vad.candidate.startedAt = now; }

function cancelInterruptionCandidate(reason) { if (!STATE.vad.candidate.isActive) return; resetVadCandidateState(); restoreTtsVolume(); }

function beginInterruptionConfirmationWindow(now) {
    STATE.vad.candidate.confirmationStartedAt = now;
    STATE.vad.candidate.confirmationExpiresAt = now + 400;
    lowerTtsVolumeForConfirmation();
    STATE.vad.candidate.loweredTts = true;
}

function resolveInterruptionConfirmation(confirmed) {
    if (!CONFIG.ENABLE_VAD_INTERRUPTION) { resetVadCandidateState(); restoreTtsVolume(); return; }
    if (confirmed) { STATE.vad.lastInterrupt = Date.now(); STATE.vad.cooldownUntil = Date.now() + 2000; interruptCurrentTurn('vad_interrupt', { captureInterruptingSpeech: true }); }
    resetVadCandidateState(); restoreTtsVolume();
}

function processInterruptionEnergySample(now, energy) {
    if (!CONFIG.ENABLE_VAD_INTERRUPTION) return;
    if (now < STATE.vad.graceUntil || now < STATE.vad.cooldownUntil) return;
    var threshold = computeDynamicInterruptionThreshold(STATE.vad.phaseMode);
    if (energy > threshold) {
        if (!STATE.vad.candidate.isActive) { startInterruptionCandidate(now); }
        else if (!STATE.vad.candidate.confirmationStartedAt) { var elapsed = now - STATE.vad.candidate.startedAt; if (elapsed > 150) beginInterruptionConfirmationWindow(now); }
        else if (now <= STATE.vad.candidate.confirmationExpiresAt) { resolveInterruptionConfirmation(true); }
    } else {
        updateVadBaseline(energy);
        if (STATE.vad.candidate.isActive) {
            if (STATE.vad.candidate.confirmationStartedAt) { if (now > STATE.vad.candidate.confirmationExpiresAt) resolveInterruptionConfirmation(false); }
            else { var candidateAge = now - STATE.vad.candidate.startedAt; if (candidateAge > 400) cancelInterruptionCandidate('energy dropped'); }
        }
    }
}

function sampleInterruptionEnergy() {
    if (!CONFIG.ENABLE_VAD_INTERRUPTION || !STATE.vad.isArmed) return;
    var energy = sampleCurrentAudioEnergy();
    STATE.vad.currentEnergy = energy; STATE.vad.lastEnergyAt = Date.now();
    processInterruptionEnergySample(Date.now(), energy);
}

function startVadEnergySampler() {
    if (!CONFIG.ENABLE_VAD_INTERRUPTION || STATE.vad.sampleTimer) return;
    STATE.vad.sampleTimer = setInterval(sampleInterruptionEnergy, 80);
}

var VADManager = {
    init: function () {
        if (STATE.vad.isLoaded) return Promise.resolve();
        return navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
            STATE.vad.monitorStream = stream;
            var ctx = new (window.AudioContext || window.webkitAudioContext)();
            STATE.vad.monitorContext = ctx;
            var source = ctx.createMediaStreamSource(stream);
            STATE.vad.monitorSource = source;
            var analyser = ctx.createAnalyser();
            analyser.fftSize = 2048;
            source.connect(analyser);
            STATE.vad.analyser = analyser;
            STATE.vad.isLoaded = true; STATE.vad.isEnabled = true;
        }).catch(function (err) { STATE.vad.disabledByFailure = true; });
    }
};


// ═══════════════════════════════════════════════════════════════
//  SECTION 4e: PHASE WATCHDOG
// ═══════════════════════════════════════════════════════════════

function startPhaseWatchdog() {
    if (STATE.voiceSafety.watchdogTimer) return;
    STATE.voiceSafety.watchdogTimer = setInterval(function () {
        if (STATE.phase === 'processing' || STATE.phase === 'speaking') {
            var elapsed = Date.now() - (STATE.vad.lastPhaseChange || Date.now());
            if (elapsed > 120000) window.hardResetVoiceState();
        }
    }, 15000);
}

window.hardResetVoiceState = function () {
    clearActiveFetchAbort(); cancelStreamingTts(); cancelBackchannelTimers(); cancelActiveBackchannel();
    stopListening(); STATE.memory.isInterrupting = false; STATE.memory.inProgressTurn = null;
    STATE.llm.isGenerating = false; STATE.llm.hasReceivedFirstToken = false;
    disarmInterruptionDetection('hard_reset'); setPhase('idle');
    toast('Voice state reset.', 'warning');
};


// ═══════════════════════════════════════════════════════════════
//  SECTION 5: TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════

function toast(message, type, duration) {
    type = type || 'info'; duration = duration || 4000;
    var icons = { success: '\u2713', error: '\u2717', warning: '\u26A0', info: '\u2139' };
    var el = document.createElement('div'); el.className = 'toast ' + type;
    el.innerHTML = '<span class="toast-icon">' + (icons[type] || '\u2139') + '</span><span>' + escapeHtml(message) + '</span>';
    DOM.toastContainer.appendChild(el);
    setTimeout(function () { el.classList.add('removing'); setTimeout(function () { el.remove(); }, 300); }, duration);
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 6: STATUS BAR & PHASE MANAGEMENT
// ═══════════════════════════════════════════════════════════════

function updateStatusDot(serviceName, status, text) {
    var el = document.getElementById('status-' + serviceName);
    if (!el) return;
    var dot = el.querySelector('.status-dot'); var txt = el.querySelector('.status-text');
    if (dot) dot.className = 'status-dot ' + status;
    if (txt) txt.textContent = text || '';
}

function setPhase(newPhase) {
    var old = STATE.phase; STATE.phase = newPhase;
    STATE.vad.lastPhaseChange = Date.now(); STATE.voiceSafety.micDisabledAt = 0;
    if (DOM.orbCanvas) DOM.orbCanvas.className = newPhase;
    var labels = { idle: 'Ready', listening: 'Listening\u2026', processing: 'Thinking\u2026', speaking: 'Speaking\u2026', interrupted: 'Interrupted\u2026' };
    if (DOM.phaseLabel) DOM.phaseLabel.textContent = labels[newPhase] || newPhase;
    if (DOM.micBtn) {
        DOM.micBtn.classList.toggle('recording', newPhase === 'listening'); DOM.micBtn.disabled = false;
        var micIcon = DOM.micBtn.querySelector('.mic-icon'); var stopIcon = DOM.micBtn.querySelector('.stop-icon');
        if (micIcon) micIcon.classList.toggle('hidden', newPhase === 'listening');
        if (stopIcon) stopIcon.classList.toggle('hidden', newPhase !== 'listening');
    }
    if (DOM.stopBtn) DOM.stopBtn.classList.toggle('hidden', newPhase !== 'processing' && newPhase !== 'speaking');
    if (!CONFIG.ENABLE_VAD_INTERRUPTION) { disarmInterruptionDetection('stability_mode'); }
    else if (newPhase === 'speaking' || newPhase === 'processing') { armInterruptionDetectionForPhase(newPhase); }
    else { disarmInterruptionDetection(newPhase); }
    if (CONFIG.ENABLE_HAPTIC_FEEDBACK && navigator.vibrate) { if (newPhase === 'listening') navigator.vibrate(30); else if (newPhase === 'idle' && old === 'speaking') navigator.vibrate([20, 40, 20]); }
}

function safeSetIdleAfterTurn(turnId) {
    if (turnId && turnId !== STATE.memory.activeTurnId) return;
    if (STATE.phase !== 'idle') setPhase('idle');
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 7: MESSAGE UI
// ═══════════════════════════════════════════════════════════════

function addMessage(role, content) {
    var id = 'msg-' + (++messageCounter); var el = document.createElement('div'); el.id = id; el.className = 'message ' + role;
    if (role === 'agent') el.innerHTML = '<div class="msg-content">' + renderMarkdownSafe(content) + '</div>';
    else if (role === 'user') el.innerHTML = '<div class="msg-content">' + escapeHtml(content) + '</div>';
    else { el.className = 'message system'; el.textContent = content; }
    DOM.messageList.appendChild(el); scrollTranscriptToBottom(); return id;
}

function createAgentMessage() {
    var id = 'msg-' + (++messageCounter); var el = document.createElement('div'); el.id = id; el.className = 'message agent';
    el.innerHTML = '<div class="msg-content"><span class="streaming-cursor"></span></div>';
    DOM.messageList.appendChild(el); scrollTranscriptToBottom(); STATE.ui.activeAgentMsgId = id; return id;
}

function updateAgentMessage(id, html, isFinal) {
    var el = document.getElementById(id); if (!el) return;
    var content = el.querySelector('.msg-content'); if (!content) return;
    content.innerHTML = isFinal ? html : html + '<span class="streaming-cursor"></span>';
    scrollTranscriptToBottom();
}

function appendSourcesTag(id, sources) {
    var el = document.getElementById(id); if (!el || !sources || !sources.length) return;
    var tag = document.createElement('div'); tag.className = 'msg-sources';
    tag.textContent = '\uD83D\uDCC1 Sources: ' + sources.join(', '); el.appendChild(tag);
}

function renderMarkdownSafe(text) {
    if (typeof marked !== 'undefined' && marked.parse) { try { return marked.parse(text); } catch (e) { } }
    return escapeHtml(text).replace(/\n/g, '<br>');
}

function scrollTranscriptToBottom() { if (DOM.transcriptArea) requestAnimationFrame(function () { DOM.transcriptArea.scrollTop = DOM.transcriptArea.scrollHeight; }); }


// ═══════════════════════════════════════════════════════════════
//  SECTION 8: ORB VISUALIZATION
// ═══════════════════════════════════════════════════════════════

function startOrbAnimation() {
    if (STATE.orb.animFrame) cancelAnimationFrame(STATE.orb.animFrame);
    var canvas = DOM.orbCanvas; if (!canvas) return;
    var ctx = canvas.getContext('2d'); var w = canvas.width; var h = canvas.height; var cx = w / 2; var cy = h / 2;
    function draw() {
        STATE.orb.tick++; ctx.clearRect(0, 0, w, h); var t = STATE.orb.tick; var level = STATE.orb.audioLevel;
        switch (STATE.phase) { case 'listening': drawListeningOrb(ctx, cx, cy, t, level); break; case 'processing': drawProcessingOrb(ctx, cx, cy, t); break; case 'ultrathinking': drawUltrathinkingOrb(ctx, cx, cy, t); break; case 'speaking': drawSpeakingOrb(ctx, cx, cy, t, level); break; default: drawIdleOrb(ctx, cx, cy, t); break; }
        STATE.orb.animFrame = requestAnimationFrame(draw);
    }
    draw();
}

function drawIdleOrb(ctx, cx, cy, t) { var pulse = 1 + 0.03 * Math.sin(t * 0.02); var r = 50 * pulse; var grad = ctx.createRadialGradient(cx, cy, r * 0.4, cx, cy, r * 1.8); grad.addColorStop(0, 'rgba(99,102,241,0.30)'); grad.addColorStop(1, 'rgba(99,102,241,0)'); ctx.fillStyle = grad; ctx.beginPath(); ctx.arc(cx, cy, r * 1.8, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = 'rgba(99,102,241,0.55)'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = 'rgba(140,143,255,0.35)'; ctx.beginPath(); ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2); ctx.fill(); }

function drawListeningOrb(ctx, cx, cy, t, lv) { var r = 50 + lv * 18; for (var i = 3; i >= 0; i--) { var rr = r + i * 12 + lv * 8; ctx.strokeStyle = 'rgba(99,102,241,' + (0.14 - i * 0.03) + ')'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, rr, 0, Math.PI * 2); ctx.stroke(); } var g = ctx.createRadialGradient(cx, cy, r * 0.3, cx, cy, r * 1.6); g.addColorStop(0, 'rgba(99,102,241,' + (0.40 + lv * 0.30) + ')'); g.addColorStop(1, 'rgba(99,102,241,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r * 1.6, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = 'rgba(99,102,241,' + (0.55 + lv * 0.30) + ')'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill(); }

function drawProcessingOrb(ctx, cx, cy, t) { var r = 50; var a = t * 0.04; var g = ctx.createRadialGradient(cx, cy, r * 0.3, cx, cy, r * 1.6); g.addColorStop(0, 'rgba(234,179,8,0.32)'); g.addColorStop(1, 'rgba(234,179,8,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r * 1.6, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = 'rgba(234,179,8,0.45)'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = 'rgba(234,179,8,0.80)'; ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(cx, cy, r + 10, a, a + Math.PI * 1.2); ctx.stroke(); ctx.strokeStyle = 'rgba(234,179,8,0.35)'; ctx.beginPath(); ctx.arc(cx, cy, r + 20, -a * 0.7, -a * 0.7 + Math.PI * 0.8); ctx.stroke(); }

function drawUltrathinkingOrb(ctx, cx, cy, t) { var r = 50 + 5 * Math.sin(t * 0.05); var a = t * 0.06; var g = ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.8); g.addColorStop(0, 'rgba(139,92,246,0.5)'); g.addColorStop(1, 'rgba(139,92,246,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r * 1.8, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = 'rgba(139,92,246,0.6)'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = 'rgba(167,139,250,0.9)'; ctx.lineWidth = 4; ctx.lineCap = 'round'; for(let i=0; i<3; i++){ ctx.beginPath(); ctx.arc(cx, cy, r + 15 + i*10, a + i*Math.PI/2, a + i*Math.PI/2 + Math.PI * 0.8); ctx.stroke(); } }

function drawSpeakingOrb(ctx, cx, cy, t, lv) { var r = 50; var g = ctx.createRadialGradient(cx, cy, r * 0.3, cx, cy, r * 1.6); g.addColorStop(0, 'rgba(34,197,94,' + (0.28 + lv * 0.20) + ')'); g.addColorStop(1, 'rgba(34,197,94,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r * 1.6, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = 'rgba(34,197,94,0.50)'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill(); var bars = 32; for (var i = 0; i < bars; i++) { var angle = (i / bars) * Math.PI * 2; var bh = 4 + Math.sin(t * 0.08 + i * 0.5) * 10 * (0.3 + lv * 0.7); var x1 = cx + Math.cos(angle) * (r + 4); var y1 = cy + Math.sin(angle) * (r + 4); var x2 = cx + Math.cos(angle) * (r + 4 + bh); var y2 = cy + Math.sin(angle) * (r + 4 + bh); ctx.strokeStyle = 'rgba(34,197,94,' + (0.35 + lv * 0.45) + ')'; ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); } }


// ═══════════════════════════════════════════════════════════════
//  SECTION 9: SPEECH-TO-TEXT ENGINE
// ═══════════════════════════════════════════════════════════════

function getAudioMimeType() {
    var types = ['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus','audio/mp4'];
    for (var i = 0; i < types.length; i++) { if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(types[i])) return types[i]; }
    return '';
}

function startListening() { 
    if (STATE.phase !== 'idle') return; 
    STATE.memory.sttSessionId++; 
    STATE.stt.predictiveTriggered = false;
    STATE.stt.lastTranscript = '';
    setPhase('listening'); 
    if (isBrowserSTT()) startBrowserSTT(); 
    else startGroqSTT(); 
}

function startBrowserSTT() {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) { toast('Speech recognition not supported.', 'error'); setPhase('idle'); return; }
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition(); var sessionId = STATE.memory.sttSessionId;
    STATE.stt.recognition = recognition; STATE.ui.currentTranscript = '';
    recognition.lang = getActiveLanguageMeta().sttBcp47; recognition.continuous = true; recognition.interimResults = true;
    var silenceTimer = null; var speechDetected = false;
    function resetSilenceTimer() { if (silenceTimer) clearTimeout(silenceTimer); if (!speechDetected) return; silenceTimer = setTimeout(function () { if (STATE.stt.isRecording) stopListening(); }, CONFIG.SILENCE_TIMEOUT_MS); }
    recognition.onstart = function () { if (STATE.phase !== 'listening' || sessionId !== STATE.memory.sttSessionId) { try { recognition.stop(); } catch (e) { } return; } STATE.stt.isRecording = true; };
    recognition.onresult = function (event) {
        if (sessionId !== STATE.memory.sttSessionId || STATE.memory.isInterrupting) return;
        var transcript = '';
        for (var i = event.resultIndex; i < event.results.length; i++) transcript += event.results[i][0].transcript;
        
        var normalized = transcript.trim();
        if (normalized === STATE.stt.lastTranscript) return;
        
        STATE.ui.currentTranscript = transcript;
        STATE.stt.lastTranscript = normalized;
        speechDetected = true;
        
        // --- 4-Tier Listener Logic ---
        resetSilenceTimer();
        handleListenerStateUpdate(normalized, sessionId);
    };

    function handleListenerStateUpdate(text, sessionId) {
        if (STATE.stt.backchannelTimer) clearTimeout(STATE.stt.backchannelTimer);
        if (STATE.stt.predictiveTimer) clearTimeout(STATE.stt.predictiveTimer);

        var isTerminal = /([.?!])$|\b(thanks|ready|done|go ahead|now|please)\b$/i.test(text);
        var isMidThought = /(and|but|or|so|because|the|a|an|my|your|his|her|its|our|their|with|at|from|into|during|including|until|against|among|throughout|despite|towards|upon|concerning|about)$/i.test(text);

        // PAUSING State: 600ms silence with mid-thought/incomplete syntax
        STATE.stt.backchannelTimer = setTimeout(function() {
            if (STATE.phase === 'listening' && !isTerminal && isMidThought) {
                triggerListeningBackchannel(sessionId);
            }
        }, 600);

        // FINISHING_LIKELY State: 300ms silence with terminal syntax
        if (isTerminal && !STATE.stt.predictiveTriggered && text.split(' ').length > 2) {
            STATE.stt.predictiveTimer = setTimeout(function() {
                if (STATE.phase === 'listening') {
                    triggerPredictiveRAG(text);
                }
            }, 300);
        }
        
        // Barge-in Ducking check
        if (STATE.phase === 'speaking') {
            PCMAudioPlayer.setVolume(0.25);
            // If it's just compliance, we'll restore later, otherwise /interrupt will kill it
            if (/^(yeah|yep|yes|mhm|okay|ok|right|i see|got it|hmm)\.?$/i.test(text)) {
                setTimeout(function() { if (STATE.phase === 'speaking') PCMAudioPlayer.setVolume(1.0); }, 1000);
            }
        }
    }

    function triggerListeningBackchannel(sessionId) {
        if (Date.now() < STATE.backchannel.cooldownUntil) return;
        fetch('/chat/backchannel/' + getOrCreateSessionId(), { method: 'POST' })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success' && data.audio) {
                    STATE.backchannel.cooldownUntil = Date.now() + 6000;
                    PCMAudioPlayer.enqueuePCMChunk(data.audio);
                }
            }).catch(e => console.warn('Backchannel fetch failed', e));
    }

    function triggerPredictiveRAG(text) {
        STATE.stt.predictiveTriggered = true;
        var body = {
            session_id: getOrCreateSessionId(),
            message: text,
            collection: getActiveCollection(),
            embed_model: STATE.embeddings.activeModel
        };
        fetch('/chat/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        }).then(r => r.json())
          .then(data => console.log('Predictive RAG status:', data.status))
          .catch(e => console.warn('Predictive RAG failed', e));
    }
    recognition.onerror = function (event) { if (sessionId !== STATE.memory.sttSessionId) return; if (event.error !== 'no-speech') toast('Speech error: ' + event.error, 'error'); if (silenceTimer) clearTimeout(silenceTimer); stopListening(); };
    recognition.onend = function () {
        if (silenceTimer) clearTimeout(silenceTimer);
        if (STATE.stt.backchannelTimer) clearTimeout(STATE.stt.backchannelTimer);
        if (STATE.stt.predictiveTimer) clearTimeout(STATE.stt.predictiveTimer);
        
        if (sessionId !== STATE.memory.sttSessionId || STATE.memory.isInterrupting) { STATE.ui.currentTranscript = ''; STATE.stt.isRecording = false; if (STATE.phase === 'listening') setPhase('idle'); return; }
        var finalTranscript = STATE.ui.currentTranscript.trim(); STATE.ui.currentTranscript = ''; STATE.stt.isRecording = false;
        if (finalTranscript) { submitUserInput(finalTranscript, 'voice'); }
        else if (STATE.phase === 'listening') setPhase('idle');
    };
    recognition.start();
}

function startGroqSTT() {
    var sessionId = STATE.memory.sttSessionId;
    navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
        if (STATE.phase !== 'listening' || sessionId !== STATE.memory.sttSessionId) { stream.getTracks().forEach(function (t) { t.stop(); }); return; }
        STATE.stt.mediaStream = stream;
        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        var source = audioCtx.createMediaStreamSource(stream); var analyser = audioCtx.createAnalyser(); analyser.fftSize = 256; source.connect(analyser);
        STATE.stt.audioContext = audioCtx; STATE.stt.analyser = analyser;
        var mime = getAudioMimeType(); STATE.stt.mimeType = mime;
        var opts = mime ? { mimeType: mime } : {};
        var recorder = new MediaRecorder(stream, opts);
        STATE.stt.mediaRecorder = recorder; STATE.stt.audioChunks = [];
        recorder.ondataavailable = function (e) { if (e.data && e.data.size > 0) STATE.stt.audioChunks.push(e.data); };
        recorder.onstop = function () { processAudioChunks(sessionId); };
        recorder.start(250); STATE.stt.isRecording = true;
        startSilenceDetection(analyser);
        STATE.stt.maxTimer = setTimeout(function () { if (STATE.stt.isRecording) stopListening(); }, CONFIG.MAX_RECORDING_MS);
    }).catch(function (err) { toast('Microphone access denied.', 'error'); setPhase('idle'); });
}

function startSilenceDetection(analyser) {
    var bufLen = analyser.frequencyBinCount; var buf = new Uint8Array(bufLen);
    var silenceStart = null; var hasDetectedSpeech = false;
    function check() {
        if (!STATE.stt.isRecording || STATE.phase !== 'listening') { STATE.orb.audioLevel = 0; return; }
        analyser.getByteFrequencyData(buf); var sum = 0; for (var i = 0; i < bufLen; i++) sum += buf[i]; var avg = sum / bufLen;
        STATE.orb.audioLevel = Math.min(avg / 100, 1);
        if (avg >= 15) { hasDetectedSpeech = true; silenceStart = null; }
        else if (hasDetectedSpeech) { if (!silenceStart) silenceStart = Date.now(); else if (Date.now() - silenceStart > CONFIG.SILENCE_TIMEOUT_MS) { stopListening(); return; } }
        requestAnimationFrame(check);
    }
    requestAnimationFrame(check);
}

function stopListening() {
    if (STATE.stt.recognition) { try { STATE.stt.recognition.stop(); } catch (e) { } STATE.stt.recognition = null; }
    if (STATE.stt.maxTimer) { clearTimeout(STATE.stt.maxTimer); STATE.stt.maxTimer = null; }
    STATE.stt.isRecording = false;
    if (STATE.stt.mediaRecorder && STATE.stt.mediaRecorder.state !== 'inactive') { try { STATE.stt.mediaRecorder.stop(); } catch (e) { } }
    if (STATE.stt.mediaStream) { STATE.stt.mediaStream.getTracks().forEach(function (t) { t.stop(); }); STATE.stt.mediaStream = null; }
    if (STATE.stt.audioContext && STATE.stt.audioContext.state !== 'closed') { STATE.stt.audioContext.close().catch(function () { }); STATE.stt.audioContext = null; STATE.stt.analyser = null; }
}

// processAudioChunks — now sends audio to backend /stt endpoint
function processAudioChunks(sessionId) {
    if (sessionId !== STATE.memory.sttSessionId || STATE.memory.isInterrupting) { STATE.stt.audioChunks = []; if (STATE.phase === 'listening' || STATE.phase === 'interrupted') safeSetIdleAfterTurn(); return; }
    var chunks = STATE.stt.audioChunks; STATE.stt.audioChunks = [];
    if (!chunks.length) { setPhase('idle'); return; }
    var mimeType = STATE.stt.mimeType || 'audio/webm';
    var blob = new Blob(chunks, { type: mimeType });
    if (blob.size < CONFIG.MIN_AUDIO_SIZE_BYTES) { setPhase('idle'); return; }
    setPhase('processing');
    var ext = mimeType.indexOf('mp4') !== -1 ? 'mp4' : mimeType.indexOf('ogg') !== -1 ? 'ogg' : 'webm';
    var formData = new FormData();
    formData.append('file', blob, 'audio.' + ext);
    formData.append('language', getActiveLanguageMeta().whisperCode);
    fetch('/stt', { method: 'POST', body: formData }).then(function (r) { if (!r.ok) throw new Error('STT error ' + r.status); return r.json(); }).then(function (data) {
        if (sessionId !== STATE.memory.sttSessionId || STATE.memory.isInterrupting) { if (STATE.phase === 'listening' || STATE.phase === 'interrupted') safeSetIdleAfterTurn(); return; }
        var text = (data.text || '').trim();
        if (!text) { setPhase('idle'); return; }
        STATE.ui.currentTranscript = text;
        submitUserInput(text, 'voice');
    }).catch(function (err) {
        if (sessionId !== STATE.memory.sttSessionId || STATE.memory.isInterrupting) return;
        toast('Speech recognition failed: ' + err.message, 'error'); setPhase('idle');
    });
}

function toggleListening() {
    if (STATE.phase === 'listening' || STATE.stt.isRecording) { stopListening(); if (STATE.phase === 'listening') setPhase('idle'); }
    else if (STATE.phase === 'idle') startListening();
    else if (STATE.phase === 'speaking' || STATE.phase === 'processing') interruptCurrentTurn('voice_restart', { restartListening: true });
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 10: TEXT PREPROCESSOR
// ═══════════════════════════════════════════════════════════════

var TextPreprocessor = {
    abbreviations: { 'Dr.': 'Doctor', 'Mr.': 'Mister', 'Mrs.': 'Missus', 'Ms.': 'Miz', 'Prof.': 'Professor', 'Jr.': 'Junior', 'Sr.': 'Senior', 'St.': 'Saint', 'vs.': 'versus', 'etc.': 'etcetera', 'approx.': 'approximately', 'dept.': 'department', 'est.': 'established', 'govt.': 'government', 'inc.': 'incorporated', 'corp.': 'corporation', 'ltd.': 'limited', 'Jan.': 'January', 'Feb.': 'February', 'Mar.': 'March', 'Apr.': 'April', 'Jun.': 'June', 'Jul.': 'July', 'Aug.': 'August', 'Sep.': 'September', 'Oct.': 'October', 'Nov.': 'November', 'Dec.': 'December', 'e.g.': 'for example', 'i.e.': 'that is', 'p.m.': 'PM', 'a.m.': 'AM' },
    stripMarkdown: function (text) { return text.replace(/```[\s\S]*?```/g, '').replace(/`([^`]+)`/g, '$1').replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1').replace(/^#{1,6}\s+/gm, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/^\s*[-*+]\s+/gm, '').replace(/^\s*\d+\.\s+/gm, '').replace(/\|/g, ', ').replace(/^[-:| ]+$/gm, '').replace(/>\s?/g, '').replace(/~~([^~]+)~~/g, '$1').trim(); },
    expandAbbreviations: function (text) { if (!CONFIG.EXPAND_ABBREVIATIONS) return text; var result = text; var abbrevs = Object.assign({}, this.abbreviations); Object.keys(abbrevs).forEach(function (abbr) { var escaped = abbr.replace(/\./g, '\\.'); result = result.replace(new RegExp('\\b' + escaped, 'g'), abbrevs[abbr]); }); return result; },
    numberToWords: function (n) { if (n === 0) return 'zero'; var ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']; var tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']; function below1000(num) { if (num < 20) return ones[num]; if (num < 100) return tens[Math.floor(num / 10)] + (num % 10 ? '-' + ones[num % 10] : ''); return ones[Math.floor(num / 100)] + ' hundred' + (num % 100 ? ' ' + below1000(num % 100) : ''); } var neg = n < 0; n = Math.abs(n); var str = ''; if (n >= 1000000000) { str += below1000(Math.floor(n / 1e9)) + ' billion '; n %= 1e9; } if (n >= 1000000) { str += below1000(Math.floor(n / 1e6)) + ' million '; n %= 1e6; } if (n >= 1000) { str += below1000(Math.floor(n / 1e3)) + ' thousand '; n %= 1e3; } if (n > 0) str += below1000(n); return (neg ? 'negative ' : '') + str.trim(); },
    normalizeNumbers: function (text) { if (!CONFIG.NUMBERS_TO_WORDS) return text; var self = this; text = text.replace(/\$([0-9,]+)(?:\.(\d+))?/g, function (m, whole, cents) { var w = parseInt(whole.replace(/,/g, ''), 10); var str = self.numberToWords(w) + ' dollar' + (w !== 1 ? 's' : ''); if (cents) { var c = parseInt(cents, 10); str += ' and ' + self.numberToWords(c) + ' cent' + (c !== 1 ? 's' : ''); } return str; }); text = text.replace(/\b([0-9]{1,3}(?:,[0-9]{3})*)\b/g, function (m) { var n = parseInt(m.replace(/,/g, ''), 10); if (n > 1900 && n < 2100) return m; if (n > 999999) return m; return self.numberToWords(n); }); return text; },
    applyCustomPronunciations: function (text) { var prons = STATE.pronunciations || {}; Object.keys(prons).forEach(function (word) { var re = new RegExp('\\b' + word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'gi'); text = text.replace(re, prons[word]); }); return text; },
    addPausesAtPunctuation: function (text) { if (!CONFIG.ADD_PAUSES) return text; text = text.replace(/;/g, ','); text = text.replace(/:/g, ','); return text; },
    normalizeSpeechSafeText: function (text) { return String(text || '').replace(/[\u2018\u2019]/g, "'").replace(/[\u201C\u201D]/g, '').replace(/[\u2013\u2014]/g, ' ').replace(/\([^)]{0,60}\)/g, '').replace(/"/g, '').replace(/&/g, ' and ').replace(/([A-Za-z])\-([A-Za-z])/g, '$1 $2').replace(/\s*\/\s*/g, ' slash ').replace(/\s+/g, ' ').trim(); },
    cleanText: function (text) { return text.replace(/\s+/g, ' ').trim(); },
    preprocess: function (text, options) {
        options = options || {}; if (!CONFIG.PREPROCESS_ENABLED) return text;
        if (isNonEnglishMode()) { var t = this.stripMarkdown(text); t = this.normalizeSpeechSafeText(t); t = this.cleanText(t); return t; }
        var t = this.stripMarkdown(text);
        if (!options.exactWording) { t = this.expandAbbreviations(t); t = this.normalizeNumbers(t); t = this.applyCustomPronunciations(t); }
        t = this.addPausesAtPunctuation(t); t = this.normalizeSpeechSafeText(t); t = this.cleanText(t); return t;
    }
};


// ═══════════════════════════════════════════════════════════════
//  SECTION 11: TTS ENGINES
// ═══════════════════════════════════════════════════════════════

var MOOD_PROSODY_TABLE = { empathetic: { pitchOffset: -0.08, rateOffset: -0.06 }, cheerful: { pitchOffset: 0.06, rateOffset: 0.04 }, urgent: { pitchOffset: 0.04, rateOffset: 0.10 }, neutral: { pitchOffset: 0, rateOffset: 0 } };
function detectMood(text) { var lower = (text || '').toLowerCase(); if (/\b(sad|sorry|unhappy|frustrated|annoyed|upset|problem|difficult|error|fail|broken|wrong)\b/.test(lower)) return 'empathetic'; if (/\b(great|awesome|excellent|perfect|happy|thank|love|wonderful|amazing)\b/.test(lower)) return 'cheerful'; if (/\b(urgent|asap|quickly|hurry|emergency)\b/.test(lower)) return 'urgent'; return 'neutral'; }
function getMoodProsody(mood) { return MOOD_PROSODY_TABLE[mood] || MOOD_PROSODY_TABLE.neutral; }

function splitIntoSentences(text) {
    var prepared = String(text || '').trim(); if (!prepared) return [];
    var matches = prepared.match(/[^.!?\n]+[.!?]+\s*|[^.!?\n]+$/g);
    if (!matches || !matches.length) return [prepared];
    return matches.map(function (s) { return s.trim(); }).filter(Boolean);
}

var NativeTTS = {
    synth: window.speechSynthesis || null,
    init: function () { var self = this; if (!self.synth) return; function load() { STATE.tts.nativeVoices = self.synth.getVoices(); populateNativeVoiceDropdown(); } load(); if (self.synth.onvoiceschanged !== undefined) self.synth.onvoiceschanged = load; },
    speak: function (text, options) {
        options = options || {}; var self = this;
        return new Promise(function (resolve, reject) {
            if (!self.synth) return reject(new Error('speechSynthesis unavailable'));
            var prepared = String(text || '').trim(); if (!prepared) { resolve(); return; }
            var sentences = options.alreadySegmented ? [prepared] : splitIntoSentences(prepared);
            if (!sentences.length) sentences = [prepared];
            var idx = 0; var settled = false;
            function finish(fn, value) { if (settled) return; settled = true; STATE.tts.currentUtterance = null; STATE.tts.speakReject = null; fn(value); }
            function speakNext() {
                if (idx >= sentences.length) { finish(resolve); return; }
                var nextText = sentences[idx++];
                var utt = new SpeechSynthesisUtterance(nextText);
                utt.rate = options.rate || CONFIG.TTS_RATE; utt.pitch = options.pitch || CONFIG.TTS_PITCH;
                utt.volume = (STATE.tts.currentVolume !== undefined) ? STATE.tts.currentVolume : 1;
                if (options.lang) utt.lang = options.lang;
                var voiceName = options.voice || CONFIG.TTS_VOICE;
                if (voiceName) { var found = STATE.tts.nativeVoices.find(function (v) { return v.name === voiceName; }); if (found) utt.voice = found; }
                utt.onend = speakNext;
                utt.onerror = function (e) { if (e.error === 'interrupted' || e.error === 'canceled') { finish(resolve); return; } finish(reject, e); };
                STATE.tts.currentUtterance = utt;
                self.synth.speak(utt);
            }
            speakNext();
            STATE.tts.speakReject = function (err) { finish(reject, err); };
        });
    },
    pause: function () { if (this.synth) this.synth.pause(); },
    resume: function () { if (this.synth) this.synth.resume(); },
    stop: function () { if (this.synth) this.synth.cancel(); },
};

var TTSManager = {
    speak: function (text, options) { STATE.tts.isSpeaking = true; return NativeTTS.speak(text, options).then(function () { STATE.tts.isSpeaking = false; }).catch(function (err) { STATE.tts.isSpeaking = false; throw err; }); },
    stop: function () { STATE.tts.isSpeaking = false; NativeTTS.stop(); },
    pause: function () { STATE.tts.isPaused = true; NativeTTS.pause(); },
    resume: function () { STATE.tts.isPaused = false; NativeTTS.resume(); },
};

function speakResponse(text, options) {
    options = options || {}; text = stripInlineSourceCitations(text);
    if (!text || !text.trim()) { if (typeof options.onComplete === 'function') options.onComplete(); setPhase('idle'); return; }
    TTSManager.stop(); setPhase('speaking');
    var prosody = getMoodProsody(detectMood(options.queryText || ''));
    var ttsOptions = { rate: Math.max(0.5, Math.min(2.0, CONFIG.TTS_RATE + prosody.rateOffset)), pitch: Math.max(0.5, Math.min(2.0, CONFIG.TTS_PITCH + prosody.pitchOffset)), voice: CONFIG.TTS_VOICE, turnId: options.turnId || null, lang: isNonEnglishMode() ? getActiveLanguageMeta().ttsLang : undefined };
    var speakable = TextPreprocessor.preprocess(buildSpokenAnswerText(text, options), ttsOptions);
    var currentSpeakId = (STATE.ui.speakId || 0) + 1; STATE.ui.speakId = currentSpeakId;
    var turnId = options.turnId || null;
    TTSManager.speak(speakable, ttsOptions).then(function () {
        if (STATE.ui.speakId !== currentSpeakId || (turnId && turnId !== STATE.memory.activeTurnId) || STATE.memory.isInterrupting) { if (typeof options.onInterrupted === 'function') options.onInterrupted(); return; }
        if (typeof options.onComplete === 'function') options.onComplete();
        safeSetIdleAfterTurn(turnId);
        if (STATE.ui.handsFreeModeActive && STATE.phase === 'idle') setTimeout(startListening, 400);
    }).catch(function () { safeSetIdleAfterTurn(turnId); });
}

function populateNativeVoiceDropdown(filter) {
    if (!DOM.ttsVoiceSelect) return;
    // CRITICAL: If server-side Kokoro voices are already loaded, do NOT overwrite them with browser voices
    if (STATE.tts.serverVoicesLoaded) {
        console.log("Skipping browser voice population as server voices are active.");
        return;
    }
    var current = DOM.ttsVoiceSelect.value;
    DOM.ttsVoiceSelect.innerHTML = '';

    var fl = (filter || '').toLowerCase();
    var filtered = STATE.tts.nativeVoices.filter(function (v) { return v.name.toLowerCase().indexOf(fl) > -1 || v.lang.toLowerCase().indexOf(fl) > -1; });
    var defaultOpt = document.createElement('option'); defaultOpt.value = ''; defaultOpt.textContent = 'Default (Browser)'; DOM.ttsVoiceSelect.appendChild(defaultOpt);
    if (!filtered.length) { var noMatch = document.createElement('option'); noMatch.value = ''; noMatch.textContent = 'No voices found'; DOM.ttsVoiceSelect.appendChild(noMatch); return; }
    var grouped = {};
    filtered.forEach(function (v) { var l = v.lang.split('-')[0].toLowerCase(); if (!grouped[l]) grouped[l] = []; grouped[l].push(v); });
    Object.keys(grouped).sort().forEach(function (lang) {
        var optgroup = document.createElement('optgroup'); optgroup.label = lang.toUpperCase();
        grouped[lang].forEach(function (v) { var opt = document.createElement('option'); opt.value = v.name; opt.textContent = v.name; optgroup.appendChild(opt); });
        DOM.ttsVoiceSelect.appendChild(optgroup);
    });
    if (current) DOM.ttsVoiceSelect.value = current;
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 12: AGENT ORCHESTRATOR (simplified — backend handles RAG/intent)
// ═══════════════════════════════════════════════════════════════

function submitUserInput(text, source) {
    text = (text || '').trim(); if (!text) return;
    var userMsgId = addMessage('user', text);
    beginInProgressTurn(text, source || 'text', userMsgId);
    if (CONFIG.ENABLE_VOICE_PIPELINE && window.voicePipelineSubmit && window.voicePipelineSubmit(text, source || 'text')) return;
    handleUserMessage(text);
}

function beginInProgressTurn(userText, source, msgId) {
    var turnId = ++STATE.memory.activeTurnId;
    STATE.memory.inProgressTurn = { id: turnId, userText: userText, source: source, msgId: msgId, startTime: Date.now() };
    STATE.llm.isGenerating = false; STATE.llm.hasReceivedFirstToken = false; STATE.llm.currentResponse = '';
    resetStreamingTtsState(turnId);
    resetBackchannelForTurn();
}

function commitInProgressTurn(turnId) {
    if (!STATE.memory.inProgressTurn || (turnId && STATE.memory.inProgressTurn.id !== turnId)) return false;
    var turn = STATE.memory.inProgressTurn;
    STATE.memory.inProgressTurn = null;
    return true;
}

function interruptCurrentTurn(reason, options) {
    options = options || {};
    STATE.memory.isInterrupting = true;
    
    // If using the LangGraph voice pipeline, notify the backend to pause/store state
    if (VoicePipeline.isActive && VoicePipeline.activeThreadId) {
        VoicePipeline.interrupt(''); // Signal interruption to backend
    }

    clearActiveFetchAbort(); 
    cancelStreamingTts(); 
    cancelBackchannelTimers(); 
    cancelActiveBackchannel();
    
    TTSManager.stop();
    if (typeof PCMAudioPlayer !== 'undefined') PCMAudioPlayer.stop();
    
    STATE.llm.isGenerating = false; 
    STATE.llm.currentResponse = '';
    
    commitInProgressTurn(STATE.memory.activeTurnId);
    
    if (options.restartListening) { 
        safeSetIdleAfterTurn(); 
        setTimeout(startListening, 200); 
    } else { 
        safeSetIdleAfterTurn(); 
    }
    
    STATE.memory.isInterrupting = false;
}

function handleUserMessage(text) {
    if (!text || !text.trim()) return;
    text = text.trim();
    var turnId = STATE.memory.inProgressTurn ? STATE.memory.inProgressTurn.id : STATE.memory.activeTurnId;
    setPhase('processing');

    // Prompt injection guard (client-side fast check; backend also checks)
    if (detectPromptInjection(text)) {
        respondWithDirectMessage(text, 'I can only help with questions about uploaded documents and general conversation.', {}, {});
        return;
    }

    // Meta-questions from history
    if (isMetaQuestion(text)) {
        respondWithDirectMessage(text, answerFromHistory(text), {}, {});
        return;
    }

    // Feedback commands
    var feedbackCmd = detectExplicitFeedbackCommand(text);
    if (feedbackCmd) {
        if (feedbackCmd === 'stop') { stopEverything(); return; }
        if (feedbackCmd === 'repeat') { var lastMsg = getLastAssistantMessageContent(); respondWithDirectMessage(text, lastMsg || "I don't have a previous response to repeat.", {}, {}); return; }
    }

    scheduleProcessingBackchannel(text, turnId);

    // ── Backend chat via SSE ──
    var agentMsgId = createAgentMessage();
    var collection = STATE.activeCollection || CONFIG.COLLECTION;
    var language = STATE.translation.activeLanguage || 'en';

    streamBackendChat(text, collection, language,
        function onToken(token, fullText) {
            // Each streaming token
            if (!STATE.llm.hasReceivedFirstToken) { STATE.llm.hasReceivedFirstToken = true; cancelBackchannelTimers(); cancelActiveBackchannel(); }
            STATE.llm.currentResponse = fullText;
            updateAgentMessage(agentMsgId, renderMarkdownSafe(fullText), false);
            pushStreamTokenToTtsBuffer(token, turnId);
        },
        function onTranslated(translatedText) {
            // Backend sent a translation of the full response
            STATE.translation.lastOriginalResponse = STATE.llm.currentResponse;
            STATE.translation.lastTranslatedResponse = translatedText;
        },
        function onSources(sources) {
            // Backend sent source list
            if (sources && sources.length) appendSourcesTag(agentMsgId, sources);
            STATE.lastRetrieval.sources = sources || [];
        },
        function onDone(fullText) {
            // Stream complete
            cancelBackchannelTimers(); cancelActiveBackchannel();
            var finalText = fullText || STATE.llm.currentResponse || '';
            finalText = stripInlineSourceCitations(finalText);
            updateAgentMessage(agentMsgId, renderMarkdownSafe(finalText), true);
            STATE.llm.isGenerating = false;

            // Flush remaining TTS buffer
            STATE.ttsStream.pendingFinalText = finalText;
            STATE.ttsStream.pendingResponseMeta = { isDocumentResponse: true, queryInfo: {} };
            flushRemainingTtsBuffer(turnId);

            // Commit to conversation memory
            STATE.memory.committedMessages.push({ role: 'user', content: text });
            STATE.memory.committedMessages.push({ role: 'assistant', content: finalText });
            while (STATE.memory.committedMessages.length > CONFIG.MEMORY_PAIRS * 2) STATE.memory.committedMessages.shift();
            syncCommittedMemory();
        },
        function onError(err) {
            cancelBackchannelTimers(); cancelActiveBackchannel();
            updateAgentMessage(agentMsgId, 'Error: ' + escapeHtml(err.message), true);
            STATE.llm.isGenerating = false;
            safeSetIdleAfterTurn(turnId);
        }
    );
}

function respondWithDirectMessage(userText, responseText, responseMeta, flags) {
    var turnId = STATE.memory.inProgressTurn ? STATE.memory.inProgressTurn.id : STATE.memory.activeTurnId;
    cancelBackchannelTimers(); cancelActiveBackchannel();
    var msgId = addMessage('agent', responseText);
    STATE.memory.committedMessages.push({ role: 'user', content: userText });
    STATE.memory.committedMessages.push({ role: 'assistant', content: responseText });
    while (STATE.memory.committedMessages.length > CONFIG.MEMORY_PAIRS * 2) STATE.memory.committedMessages.shift();
    syncCommittedMemory();
    commitInProgressTurn(turnId);
    var speakOpts = { turnId: turnId, queryText: userText, responseMeta: responseMeta };
    speakResponse(responseText, speakOpts);
}

// ── Backend SSE Streaming ──────────────────────────────────────
function streamBackendChat(userMessage, collection, language, onToken, onTranslated, onSources, onDone, onError) {
    var controller = new AbortController();
    STATE.llm.abortController = controller;
    STATE.llm.isGenerating = true;
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: getOrCreateSessionId(),
            message: userMessage,
            collection: collection || CONFIG.COLLECTION,
            language: language || 'en',
            stream: true,
            chat_model: STATE.llm.activeChatModel || undefined,
            chat_provider: STATE.llm.activeChatProvider || undefined,
            embed_model: STATE.embeddings.activeModel || undefined
        }),
        signal: controller.signal
    }).then(function (resp) {
        if (!resp.ok) throw new Error('Backend error ' + resp.status);
        var reader = resp.body.getReader();
        var decoder = new TextDecoder();
        var full = '';
        function pump() {
            return reader.read().then(function (result) {
                if (result.done) { onDone(full); return; }
                var chunk = decoder.decode(result.value, { stream: true });
                var lines = chunk.split('\n');
                lines.forEach(function (line) {
                    if (!line.startsWith('data: ')) return;
                    var payload = line.slice(6).trim();
                    if (payload === '[DONE]') { onDone(full); return; }
                    try {
                        var obj = JSON.parse(payload);
                        if (obj.token) { full += obj.token; onToken(obj.token, full); }
                        if (obj.translated) onTranslated(obj.translated);
                        if (obj.sources) onSources(obj.sources);
                    } catch (e) { }
                });
                return pump();
            });
        }
        return pump();
    }).catch(function (err) {
        if (err.name === 'AbortError') return;
        onError(err);
    });
}

function handleTypedMessage() {
    if (!DOM.textInput) return;
    var text = DOM.textInput.value.trim(); if (!text) return;
    if (STATE.phase === 'processing' || STATE.phase === 'speaking') { interruptCurrentTurn('text_submit', { restartListening: false }); STATE.memory.isInterrupting = false; safeSetIdleAfterTurn(); }
    else if (STATE.phase !== 'idle') return;
    DOM.textInput.value = ''; DOM.textInput.style.height = 'auto';
    submitUserInput(text, 'text');
}

function stopEverything() { interruptCurrentTurn('explicit_stop', { restartListening: false, suppressReply: true }); }


// ═══════════════════════════════════════════════════════════════
//  SECTION 13: DOCUMENT MANAGER UI (now calls /ingest)
// ═══════════════════════════════════════════════════════════════

function handleFileSelect(event) { var file = event.target.files && event.target.files[0]; if (!file) return; event.target.value = ''; startIngestion(file); }
function handleFileDrop(event) { event.preventDefault(); if (DOM.dropZone) DOM.dropZone.classList.remove('drag-over'); var files = event.dataTransfer && event.dataTransfer.files; if (!files || !files.length) return; startIngestion(files[0]); }

function startIngestion(file) {
    var validExts = ['.pdf', '.docx', '.txt', '.csv'];
    var lower = file.name.toLowerCase();
    var valid = validExts.some(function (ext) { return lower.endsWith(ext); });
    if (!valid) { toast('Unsupported file type. Use PDF, DOCX, TXT, or CSV.', 'error'); return; }
    if (STATE.documents.isIngesting) { toast('Already processing a file. Please wait.', 'warning'); return; }

    STATE.documents.isIngesting = true;
    openDocumentsPanel();
    showIngestionProgress(true);
    updateProgress(10, 'Uploading ' + file.name + '\u2026');

    var formData = new FormData();
    formData.append('file', file);
    formData.append('collection', getActiveCollection());
    if (STATE.embeddings.activeModel) formData.append('embed_model', STATE.embeddings.activeModel);

    fetch('/ingest', { method: 'POST', body: formData }).then(function (r) {
        if (!r.ok) return r.json().then(function (d) { throw new Error((d.detail) || 'Ingest error ' + r.status); });
        return r.json();
    }).then(function (data) {
        updateProgress(100, 'Done! ' + data.chunks_created + ' chunks stored.');
        setTimeout(function () { showIngestionProgress(false); }, 1500);
        STATE.documents.ingested.push({ filename: data.filename, chunks: data.chunks_created, uploadedAt: Date.now() });
        saveDocumentsForCollection(getActiveCollection(), STATE.documents.ingested);
        renderDocumentList();
        toast(file.name + ' processed successfully!', 'success');
        addMessage('agent', 'I have processed ' + file.name + ' and stored ' + data.chunks_created + ' text chunks. You can now ask me questions about it.');
        speakResponse('I have processed your document and I am ready to answer questions about it.');
    }).catch(function (err) {
        showIngestionProgress(false);
        toast('Ingestion failed: ' + err.message, 'error');
    }).finally(function () { STATE.documents.isIngesting = false; });
}

function updateProgress(pct, text) { if (DOM.progressBar) DOM.progressBar.style.width = pct + '%'; if (DOM.progressText) DOM.progressText.textContent = text; }
function showIngestionProgress(show) { if (DOM.ingestionProgress) DOM.ingestionProgress.classList.toggle('hidden', !show); }

function renderDocumentList() {
    if (!DOM.documentList) return;
    var docs = STATE.documents.ingested;
    if (!docs.length) { DOM.documentList.innerHTML = '<p class="empty-state">No documents uploaded yet.</p>'; return; }
    DOM.documentList.innerHTML = '';
    docs.forEach(function (doc, idx) {
        var card = document.createElement('div'); card.className = 'document-card';
        var date = doc.uploadedAt ? new Date(doc.uploadedAt).toLocaleDateString() : '';
        var ext = doc.filename.split('.').pop().toUpperCase();
        card.innerHTML = '<div class="doc-icon">' + ext + '</div><div class="doc-info"><div class="doc-name" title="' + escapeHtml(doc.filename) + '">' + escapeHtml(doc.filename) + '</div><div class="doc-meta">' + doc.chunks + ' chunks \xB7 ' + date + '</div></div><button class="doc-delete" title="Remove document" data-idx="' + idx + '">\xD7</button>';
        card.querySelector('.doc-delete').addEventListener('click', function (e) { deleteDocument(parseInt(e.target.dataset.idx, 10)); });
        DOM.documentList.appendChild(card);
    });
}

function deleteDocument(idx) {
    var doc = STATE.documents.ingested[idx]; if (!doc) return;
    fetch('/collections/' + getActiveCollection() + '/documents/' + encodeURIComponent(doc.filename), { method: 'DELETE' }).then(function (r) { if (!r.ok) throw new Error('Delete failed'); return r.json(); }).then(function () {
        STATE.documents.ingested.splice(idx, 1);
        saveDocumentsForCollection(getActiveCollection(), STATE.documents.ingested);
        renderDocumentList(); toast(doc.filename + ' removed.', 'success');
    }).catch(function (err) { toast('Failed to delete: ' + err.message, 'error'); });
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 14: PANEL MANAGEMENT
// ═══════════════════════════════════════════════════════════════

function openSettingsPanel() { STATE.ui.settingsPanelOpen = true; if (DOM.settingsPanel) { DOM.settingsPanel.classList.remove('hidden'); requestAnimationFrame(function () { DOM.settingsPanel.classList.add('visible'); }); } if (DOM.settingsOverlay) { DOM.settingsOverlay.classList.remove('hidden'); requestAnimationFrame(function () { DOM.settingsOverlay.classList.add('visible'); }); } }
function closeSettingsPanel() { STATE.ui.settingsPanelOpen = false; if (DOM.settingsPanel) DOM.settingsPanel.classList.remove('visible'); if (DOM.settingsOverlay) DOM.settingsOverlay.classList.remove('visible'); setTimeout(function () { if (!STATE.ui.settingsPanelOpen) { if (DOM.settingsPanel) DOM.settingsPanel.classList.add('hidden'); if (DOM.settingsOverlay) DOM.settingsOverlay.classList.add('hidden'); } }, 350); }
function openDocumentsPanel() { STATE.ui.documentsPanelOpen = true; if (DOM.documentsPanel) { DOM.documentsPanel.classList.remove('hidden'); requestAnimationFrame(function () { DOM.documentsPanel.classList.add('visible'); }); } if (DOM.documentsOverlay) { DOM.documentsOverlay.classList.remove('hidden'); requestAnimationFrame(function () { DOM.documentsOverlay.classList.add('visible'); }); } }
function closeDocumentsPanel() { STATE.ui.documentsPanelOpen = false; if (DOM.documentsPanel) DOM.documentsPanel.classList.remove('visible'); if (DOM.documentsOverlay) DOM.documentsOverlay.classList.remove('visible'); setTimeout(function () { if (!STATE.ui.documentsPanelOpen) { if (DOM.documentsPanel) DOM.documentsPanel.classList.add('hidden'); if (DOM.documentsOverlay) DOM.documentsOverlay.classList.add('hidden'); } }, 350); }
function openHistoryPanel() { STATE.ui.historyPanelOpen = true; renderHistoryList(); if (DOM.historyPanel) { DOM.historyPanel.classList.remove('hidden'); requestAnimationFrame(function () { DOM.historyPanel.classList.add('visible'); }); } if (DOM.historyOverlay) { DOM.historyOverlay.classList.remove('hidden'); requestAnimationFrame(function () { DOM.historyOverlay.classList.add('visible'); }); } }
function closeHistoryPanel() { STATE.ui.historyPanelOpen = false; if (DOM.historyPanel) DOM.historyPanel.classList.remove('visible'); if (DOM.historyOverlay) DOM.historyOverlay.classList.remove('visible'); setTimeout(function () { if (!STATE.ui.historyPanelOpen) { if (DOM.historyPanel) DOM.historyPanel.classList.add('hidden'); if (DOM.historyOverlay) DOM.historyOverlay.classList.add('hidden'); } }, 350); }

function renderHistoryList() {
    if (!DOM.historyList) return;
    var sessions = STATE.conversation.sessions;
    if (!sessions.length) { DOM.historyList.innerHTML = '<p class="empty-state">No past conversations yet.</p>'; return; }
    DOM.historyList.innerHTML = '';
    sessions.slice().sort(function (a, b) { return b.timestamp - a.timestamp; }).forEach(function (session) {
        var card = document.createElement('div'); card.className = 'document-card';
        var date = session.timestamp ? new Date(session.timestamp).toLocaleString() : '';
        var msgCount = session.history ? session.history.length : 0;
        var titlePreview = session.preview || 'Conversation';
        card.innerHTML = '<div class="doc-icon">\uD83D\uDD52</div><div class="doc-info" style="cursor:pointer;"><div class="doc-name">' + escapeHtml(titlePreview) + '</div><div class="doc-meta">' + msgCount + ' messages \xB7 ' + date + '</div></div><button class="doc-delete" title="Delete session" data-id="' + session.id + '">\xD7</button>';
        card.querySelector('.doc-info').addEventListener('click', function () { loadSession(session.id); closeHistoryPanel(); if (STATE.ui.settingsPanelOpen) closeSettingsPanel(); });
        card.querySelector('.doc-delete').addEventListener('click', function (e) { e.stopPropagation(); deleteSession(session.id); });
        DOM.historyList.appendChild(card);
    });
}

function saveActiveSession() {
    if (STATE.memory.committedMessages.length === 0) return;
    var preview = 'Empty Chat';
    var firstUserMsg = STATE.memory.committedMessages.find(function (m) { return m.role === 'user'; });
    if (firstUserMsg && firstUserMsg.content) { preview = firstUserMsg.content; if (preview.length > 40) preview = preview.substring(0, 37) + '...'; }
    var existingIdx = STATE.conversation.sessions.findIndex(function (s) { return s.id === STATE.conversation.currentSessionId; });
    var sessionData = { id: STATE.conversation.currentSessionId, timestamp: Date.now(), preview: preview, history: cloneMessages(STATE.memory.committedMessages), lastRetrieval: cloneRetrieval(STATE.lastRetrieval), collection: getActiveCollection() };
    if (existingIdx !== -1) STATE.conversation.sessions[existingIdx] = sessionData; else STATE.conversation.sessions.push(sessionData);
    saveSessionsForCollection(getActiveCollection(), STATE.conversation.sessions);
}

function recoverInteractiveIdleState(reason) {
    clearActiveFetchAbort(); cancelStreamingTts(); cancelBackchannelTimers(); cancelActiveBackchannel();
    TTSManager.stop(); stopListening();
    STATE.memory.isInterrupting = false; STATE.memory.inProgressTurn = null;
    STATE.llm.isGenerating = false; STATE.llm.abortController = null; STATE.llm.hasReceivedFirstToken = false; STATE.llm.currentResponse = '';
    disarmInterruptionDetection('conversation_reset');
    safeSetIdleAfterTurn(); if (STATE.phase !== 'idle') setPhase('idle');
}

function startNewChat() {
    recoverInteractiveIdleState('start_new_chat'); saveActiveSession();
    STATE.conversation.history = []; STATE.conversation.turnCount = 0; STATE.lastIntentWasDocument = false;
    resetLastRetrievalState(); initializeCommittedMemory();
    STATE.conversation.currentSessionId = 'session_' + Date.now();
    persistActiveCollectionConversation(); persistActiveCollectionRetrieval();
    saveSessionIdForCollection(getActiveCollection(), STATE.conversation.currentSessionId);
    if (DOM.messageList) DOM.messageList.innerHTML = '';
    toast('Started a new conversation.', 'success');
}

function loadSession(id) {
    recoverInteractiveIdleState('load_session'); saveActiveSession();
    var session = STATE.conversation.sessions.find(function (s) { return s.id === id; }); if (!session) return;
    STATE.conversation.currentSessionId = id;
    saveSessionIdForCollection(getActiveCollection(), id);
    STATE.conversation.history = JSON.parse(JSON.stringify(session.history));
    STATE.conversation.turnCount = STATE.conversation.history.length;
    STATE.lastRetrieval = Object.assign(createEmptyLastRetrieval(), session.lastRetrieval || {});
    STATE.lastIntentWasDocument = !!(STATE.lastRetrieval.resolvedQuery || STATE.lastRetrieval.answer);
    initializeCommittedMemory(); persistActiveCollectionConversation(); persistActiveCollectionRetrieval();
    renderConversationToUi(); toast('Session loaded.', 'success');
}

function deleteSession(id) {
    if (!confirm('Delete this conversation?')) return;
    recoverInteractiveIdleState('delete_session');
    STATE.conversation.sessions = STATE.conversation.sessions.filter(function (s) { return s.id !== id; });
    saveSessionsForCollection(getActiveCollection(), STATE.conversation.sessions);
    if (id === STATE.conversation.currentSessionId) startNewChat();
    renderHistoryList();
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 15: SETTINGS PERSISTENCE
// ═══════════════════════════════════════════════════════════════

function updateLanguageIndicator() {
    if (!DOM.languageIndicator || !DOM.activeLanguageLabel) return;
    if (STATE.translation.activeLanguage !== 'en') { DOM.languageIndicator.classList.remove('hidden'); DOM.activeLanguageLabel.textContent = getActiveLanguageMeta().name; }
    else DOM.languageIndicator.classList.add('hidden');
}

function loadSettings() {
    resetLegacyLocalStateIfNeeded();
    var rate = parseFloat(loadFromStorage('tts_rate', CONFIG.TTS_RATE)); CONFIG.TTS_RATE = rate; if (DOM.ttsRateSlider) { DOM.ttsRateSlider.value = rate; if (DOM.ttsRateValue) DOM.ttsRateValue.textContent = rate.toFixed(1); }
    var pitch = parseFloat(loadFromStorage('tts_pitch', CONFIG.TTS_PITCH)); CONFIG.TTS_PITCH = pitch; if (DOM.ttsPitchSlider) { DOM.ttsPitchSlider.value = pitch; if (DOM.ttsPitchValue) DOM.ttsPitchValue.textContent = pitch.toFixed(1); }
    CONFIG.TTS_VOICE = loadFromStorage('tts_voice', CONFIG.TTS_VOICE);
    CONFIG.STT_ENGINE = loadFromStorage('stt_engine', CONFIG.STT_ENGINE); if (DOM.sttEngineSelect) DOM.sttEngineSelect.value = CONFIG.STT_ENGINE;
    var lang = loadFromStorage('stt_language', CONFIG.STT_LANGUAGE); CONFIG.STT_LANGUAGE = lang; if (DOM.sttLanguageSelect) DOM.sttLanguageSelect.value = lang; STATE.translation.activeLanguage = lang; updateLanguageIndicator();
    var silence = parseInt(loadFromStorage('silence_timeout', CONFIG.SILENCE_TIMEOUT_MS), 10); CONFIG.SILENCE_TIMEOUT_MS = silence; if (DOM.silenceTimeoutSlider) { DOM.silenceTimeoutSlider.value = silence; if (DOM.silenceTimeoutValue) DOM.silenceTimeoutValue.textContent = (silence / 1000).toFixed(1) + 's'; }
    STATE.feedback.responseLengthPreference = loadFromStorage('response_length_pref', 'normal');
    var savedCollection = loadFromStorage('active_collection', CONFIG.COLLECTION); STATE.activeCollection = savedCollection;
    var hf = loadFromStorage('handsfree', false); STATE.ui.handsFreeModeActive = hf; if (DOM.handsfreeToggle) DOM.handsfreeToggle.checked = hf;
    STATE.pronunciations = loadFromStorage('pronunciations', {}); renderPronunciationList();
    STATE.documents.ingested = loadDocumentsForCollection(savedCollection);
    STATE.conversation.history = loadConversationForCollection(savedCollection); STATE.conversation.turnCount = STATE.conversation.history.length;
    STATE.conversation.sessions = loadSessionsForCollection(savedCollection);
    STATE.conversation.currentSessionId = ensureCollectionSessionId(savedCollection);
    STATE.lastRetrieval = loadRetrievalForCollection(savedCollection) || createEmptyLastRetrieval();
    STATE.lastIntentWasDocument = !!(STATE.lastRetrieval && (STATE.lastRetrieval.resolvedQuery || STATE.lastRetrieval.answer));
    
    // Model settings
    STATE.llm.activeChatModel = loadFromStorage('active_chat_model', '');
    STATE.llm.activeChatProvider = loadFromStorage('active_chat_provider', '');
    STATE.embeddings.activeModel = loadFromStorage('active_embed_model', '');
    
    // TTS settings
    CONFIG.TTS_VOICE = loadFromStorage('tts_voice', 'af_heart');
    if (DOM.ttsVoiceSelect) DOM.ttsVoiceSelect.value = CONFIG.TTS_VOICE;
    CONFIG.TTS_HARDWARE = loadFromStorage('tts_hardware', 'gpu');
    if (DOM.ttsHardwareSelect) DOM.ttsHardwareSelect.value = CONFIG.TTS_HARDWARE;

    initializeCommittedMemory();

}

function renderPronunciationList() {
    if (!DOM.pronunciationList) return;
    var prons = STATE.pronunciations; var keys = Object.keys(prons);
    if (!keys.length) { DOM.pronunciationList.innerHTML = '<p class="empty-state" style="font-size:12px">No custom pronunciations.</p>'; return; }
    DOM.pronunciationList.innerHTML = '';
    keys.forEach(function (word) {
        var entry = document.createElement('div'); entry.className = 'pronunciation-entry';
        entry.innerHTML = '<span class="pron-word">' + escapeHtml(word) + '</span><span class="pron-arrow">\u2192</span><span class="pron-replacement">' + escapeHtml(prons[word]) + '</span><button class="pron-delete" data-word="' + escapeHtml(word) + '" title="Remove">\xD7</button>';
        entry.querySelector('.pron-delete').addEventListener('click', function (e) { var w = e.target.dataset.word; delete STATE.pronunciations[w]; saveToStorage('pronunciations', STATE.pronunciations); renderPronunciationList(); });
        DOM.pronunciationList.appendChild(entry);
    });
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 16: BOOT / HEALTH CHECKS (now calls /health)
// ═══════════════════════════════════════════════════════════════

function shouldShowBootGreeting() {
    if (STATE.conversation.history && STATE.conversation.history.length > 0) return false;
    if (DOM.messageList && DOM.messageList.children && DOM.messageList.children.length > 0) return false;
    return true;
}

function fetchModelsAndPopulate() {
    return fetch('/models').then(function (r) { if (!r.ok) throw new Error('Models error'); return r.json(); }).then(function (data) {
        // Chat Models
        if (DOM.chatModelSelect) {
            DOM.chatModelSelect.innerHTML = '<option value="">Server-managed</option>';
            var cm = data.chat || {};
            if (cm.ollama && cm.ollama.length) {
                var g = document.createElement('optgroup'); g.label = 'Ollama (Local)';
                cm.ollama.forEach(function (m) { var o = document.createElement('option'); o.value = 'ollama|' + m; o.textContent = m; g.appendChild(o); });
                DOM.chatModelSelect.appendChild(g);
            }
            if (cm.groq && cm.groq.length) {
                var g = document.createElement('optgroup'); g.label = 'Groq (Cloud)';
                cm.groq.forEach(function (m) { var o = document.createElement('option'); o.value = 'groq|' + m; o.textContent = m; g.appendChild(o); });
                DOM.chatModelSelect.appendChild(g);
            }
            DOM.chatModelSelect.disabled = false;
            var current = STATE.llm.activeChatProvider + '|' + STATE.llm.activeChatModel;
            if (STATE.llm.activeChatModel && STATE.llm.activeChatProvider) DOM.chatModelSelect.value = current;
        }
        // Embed Models
        if (DOM.embedModelSelect) {
            DOM.embedModelSelect.innerHTML = '<option value="">Server-managed</option>';
            var em = data.embeddings || {};
            if (em.ollama && em.ollama.length) {
                var g = document.createElement('optgroup'); g.label = 'Ollama (Embed)';
                em.ollama.forEach(function (m) { var o = document.createElement('option'); o.value = m; o.textContent = m; g.appendChild(o); });
                DOM.embedModelSelect.appendChild(g);
            }
            DOM.embedModelSelect.disabled = false;
            if (STATE.embeddings.activeModel) DOM.embedModelSelect.value = STATE.embeddings.activeModel;
        }

        // TTS Voices
        if (DOM.ttsVoiceSelect && data.tts && data.tts.voices) {
            var voices = data.tts.voices;
            DOM.ttsVoiceSelect.innerHTML = '';
            voices.forEach(function(v) {
                var o = document.createElement('option');
                o.value = v;
                o.textContent = v;
                DOM.ttsVoiceSelect.appendChild(o);
            });
            STATE.tts.serverVoicesLoaded = true; // Set flag to block browser overwrite
            if (CONFIG.TTS_VOICE) DOM.ttsVoiceSelect.value = CONFIG.TTS_VOICE;
        }

        
        // TTS Hardware
        if (DOM.ttsHardwareSelect && data.tts && data.tts.hardware) {
            var hw = data.tts.hardware;
            var gpuOpt = DOM.ttsHardwareSelect.querySelector('option[value="gpu"]');
            if (gpuOpt) {
                if (hw.gpu) {
                    gpuOpt.textContent = 'GPU (Active - NVIDIA)';
                } else {
                    gpuOpt.textContent = 'GPU (Unavailable)';
                    gpuOpt.disabled = true;
                    if (CONFIG.TTS_HARDWARE === 'gpu') {
                        CONFIG.TTS_HARDWARE = 'cpu';
                        DOM.ttsHardwareSelect.value = 'cpu';
                    }
                }
            }
        }
    });
}


function fetchCollectionsAndPopulate() {
    return fetch('/collections').then(function (r) { if (!r.ok) throw new Error('Collections error'); return r.json(); }).then(function (data) {
        var names = data.collections || [];
        [DOM.collectionSelect, DOM.settingsCollectionSelect].forEach(function (sel) {
            if (!sel) return; sel.innerHTML = '';
            names.forEach(function (n) { var opt = document.createElement('option'); opt.value = n; opt.textContent = n; sel.appendChild(opt); });
            var current = getActiveCollection();
            if (names.indexOf(current) !== -1) sel.value = current;
            sel.disabled = false;
        });
    });
}

function ensureCollection() {
    var col = getActiveCollection();
    return fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: col }) }).then(function (r) { if (!r.ok) return r.json().then(function (d) { throw new Error(d.detail || 'Create failed'); }); return r.json(); }).then(function () { STATE.services.qdrant.collectionReady = true; }).catch(function (err) { console.warn('ensureCollection:', err.message); });
}

function onCollectionChange(e) {
    var col = e.target.value; if (!col) return;
    saveActiveSession();
    STATE.activeCollection = col; saveToStorage('active_collection', col);
    STATE.documents.ingested = loadDocumentsForCollection(col); renderDocumentList();
    STATE.conversation.history = loadConversationForCollection(col); STATE.conversation.turnCount = STATE.conversation.history.length;
    STATE.conversation.sessions = loadSessionsForCollection(col);
    STATE.conversation.currentSessionId = ensureCollectionSessionId(col);
    STATE.lastRetrieval = loadRetrievalForCollection(col) || createEmptyLastRetrieval();
    STATE.lastIntentWasDocument = !!(STATE.lastRetrieval && (STATE.lastRetrieval.resolvedQuery || STATE.lastRetrieval.answer));
    initializeCommittedMemory(); persistActiveCollectionConversation(); persistActiveCollectionRetrieval();
    renderConversationToUi();
    [DOM.collectionSelect, DOM.settingsCollectionSelect].forEach(function (sel) { if (sel) sel.value = col; });
}

function confirmNewCollection() {
    if (!DOM.newCollectionInput) return; var name = DOM.newCollectionInput.value.trim(); if (!name) return;
    fetch('/collections', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name }) }).then(function (r) { if (!r.ok) throw new Error('Create failed'); return r.json(); }).then(function () {
        toast('Collection "' + name + '" created.', 'success');
        DOM.newCollectionInput.value = ''; if (DOM.newCollectionRow) DOM.newCollectionRow.classList.add('hidden');
        fetchCollectionsAndPopulate().then(function () { STATE.activeCollection = name; saveToStorage('active_collection', name); [DOM.collectionSelect, DOM.settingsCollectionSelect].forEach(function (sel) { if (sel) sel.value = name; }); onCollectionChange({ target: { value: name } }); });
    }).catch(function (err) { toast('Create failed: ' + err.message, 'error'); });
}

function cancelNewCollection() { if (DOM.newCollectionInput) DOM.newCollectionInput.value = ''; if (DOM.newCollectionRow) DOM.newCollectionRow.classList.add('hidden'); }

function boot() {
    updateStatusDot('ollama', 'warning', 'Checking\u2026'); updateStatusDot('qdrant', 'warning', 'Checking\u2026'); updateStatusDot('groq', 'warning', 'Checking\u2026');
    return fetch('/health').then(function (r) { if (!r.ok) throw new Error('Health check failed'); return r.json(); }).then(function (data) {
        if (data.ollama && data.ollama.online) { STATE.services.ollama.online = true; updateStatusDot('ollama', 'online', 'Online'); } else { updateStatusDot('ollama', 'offline', 'Offline'); }
        if (data.qdrant && data.qdrant.online) { STATE.services.qdrant.online = true; updateStatusDot('qdrant', 'online', 'Online'); } else { updateStatusDot('qdrant', 'offline', 'Offline'); }
        if (data.groq && data.groq.online) { STATE.services.groq.online = true; updateStatusDot('groq', 'online', 'Online'); } else { updateStatusDot('groq', 'offline', 'Offline'); }
        STATE.allReady = STATE.services.ollama.online || STATE.services.groq.online;
        setPhase('idle');
        if (STATE.allReady && shouldShowBootGreeting()) {
            var hour = new Date().getHours();
            var timeGreet = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
            var greet = timeGreet + "! I'm your document assistant. You can speak to me or upload a document. How can I help?";
            addMessage('agent', greet); speakResponse(greet);
        } else if (!STATE.allReady) {
            addMessage('system', 'Some services are offline. Check the status bar.');
        }
        return fetchModelsAndPopulate().catch(function(e){ console.warn('Models offline:', e); })
            .then(function () { return fetchCollectionsAndPopulate().catch(function(e){ console.warn('Collections offline:', e); }); })
            .then(function () { return ensureCollection().catch(function(e){ console.warn('EnsureCollection failed:', e); }); });
    }).then(function () {
        renderDocumentList();
        VADManager.init().catch(function (err) { console.warn('[Boot] VAD init failed (non-fatal):', err); });
        startPhaseWatchdog();
    }).catch(function (err) {
        console.error('Boot error:', err);
        if (isAuthError(err)) {
            AUTH.clear();
            showAuthModal();
            setAuthError('Your session expired. Please sign in again.');
            setPhase('idle');
            return;
        }
        // If /health itself fails, we are really offline
        updateStatusDot('ollama', 'offline', 'Offline'); updateStatusDot('qdrant', 'offline', 'Offline'); updateStatusDot('groq', 'offline', 'Offline');
        setPhase('idle'); 
        addMessage('system', 'Backend connection lost or unstable. Attempting to proceed...');
    });
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 17: EVENT BINDING
// ═══════════════════════════════════════════════════════════════

function bindEvents() {
    if (DOM.micBtn) DOM.micBtn.addEventListener('click', toggleListening);
    if (DOM.stopBtn) DOM.stopBtn.addEventListener('click', stopEverything);
    if (DOM.uploadBtn) DOM.uploadBtn.addEventListener('click', function () { if (DOM.fileInput) DOM.fileInput.click(); });
    if (DOM.fileInput) DOM.fileInput.addEventListener('change', handleFileSelect);
    if (DOM.docsBtn) DOM.docsBtn.addEventListener('click', function () { STATE.ui.documentsPanelOpen ? closeDocumentsPanel() : openDocumentsPanel(); });
    if (DOM.textInput) {
        DOM.textInput.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleTypedMessage(); } });
        DOM.textInput.addEventListener('input', function () { this.style.height = 'auto'; this.style.height = Math.min(this.scrollHeight, 120) + 'px'; });
    }
    if (DOM.sendBtn) DOM.sendBtn.addEventListener('click', handleTypedMessage);
    if (DOM.handsfreeToggle) DOM.handsfreeToggle.addEventListener('change', function () { STATE.ui.handsFreeModeActive = this.checked; saveToStorage('handsfree', this.checked); if (this.checked && STATE.phase === 'idle') startListening(); });
    if (DOM.settingsBtn) DOM.settingsBtn.addEventListener('click', function () { STATE.ui.settingsPanelOpen ? closeSettingsPanel() : openSettingsPanel(); });
    if (DOM.settingsClose) DOM.settingsClose.addEventListener('click', closeSettingsPanel);
    if (DOM.settingsOverlay) DOM.settingsOverlay.addEventListener('click', closeSettingsPanel);
    if (DOM.historyBtn) DOM.historyBtn.addEventListener('click', function () { STATE.ui.historyPanelOpen ? closeHistoryPanel() : openHistoryPanel(); });
    if (DOM.historyClose) DOM.historyClose.addEventListener('click', closeHistoryPanel);
    if (DOM.historyOverlay) DOM.historyOverlay.addEventListener('click', closeHistoryPanel);
    if (DOM.documentsClose) DOM.documentsClose.addEventListener('click', closeDocumentsPanel);
    if (DOM.documentsOverlay) DOM.documentsOverlay.addEventListener('click', closeDocumentsPanel);
    if (DOM.dropZone) {
        DOM.dropZone.addEventListener('dragover', function (e) { e.preventDefault(); this.classList.add('drag-over'); });
        DOM.dropZone.addEventListener('dragleave', function () { this.classList.remove('drag-over'); });
        DOM.dropZone.addEventListener('drop', handleFileDrop);
        DOM.dropZone.addEventListener('click', function () { if (DOM.fileInput) DOM.fileInput.click(); });
    }
    if (DOM.ttsVoiceSelect) DOM.ttsVoiceSelect.addEventListener('change', function () { CONFIG.TTS_VOICE = this.value; saveToStorage('tts_voice', this.value); });
    if (DOM.ttsRateSlider) DOM.ttsRateSlider.addEventListener('input', function () { var v = parseFloat(this.value); CONFIG.TTS_RATE = v; saveToStorage('tts_rate', v); if (DOM.ttsRateValue) DOM.ttsRateValue.textContent = v.toFixed(1); });
    if (DOM.ttsPitchSlider) DOM.ttsPitchSlider.addEventListener('input', function () { var v = parseFloat(this.value); CONFIG.TTS_PITCH = v; saveToStorage('tts_pitch', v); if (DOM.ttsPitchValue) DOM.ttsPitchValue.textContent = v.toFixed(1); });
    
    // New TTS Controls
    if (DOM.ttsHardwareSelect) DOM.ttsHardwareSelect.addEventListener('change', function() { CONFIG.TTS_HARDWARE = this.value; saveToStorage('tts_hardware', this.value); toast('Hardware updated to ' + this.value, 'info'); });
    if (DOM.ttsVoiceSearch) DOM.ttsVoiceSearch.addEventListener('input', function() {
        var term = this.value.toLowerCase();
        if (!DOM.ttsVoiceSelect) return;
        Array.from(DOM.ttsVoiceSelect.options).forEach(function(opt) {
            var visible = opt.value.toLowerCase().indexOf(term) !== -1;
            opt.style.display = visible ? '' : 'none';
        });
    });

    if (DOM.sttLanguageSelect) DOM.sttLanguageSelect.addEventListener('change', function () { CONFIG.STT_LANGUAGE = this.value; saveToStorage('stt_language', this.value); STATE.translation.activeLanguage = this.value; updateLanguageIndicator(); toast('Language: ' + (LANGUAGE_META[this.value] || {}).name, 'info'); });

    if (DOM.sttEngineSelect) DOM.sttEngineSelect.addEventListener('change', function () { CONFIG.STT_ENGINE = this.value; saveToStorage('stt_engine', this.value); });
    if (DOM.silenceTimeoutSlider) DOM.silenceTimeoutSlider.addEventListener('input', function () { var v = parseInt(this.value, 10); CONFIG.SILENCE_TIMEOUT_MS = v; saveToStorage('silence_timeout', v); if (DOM.silenceTimeoutValue) DOM.silenceTimeoutValue.textContent = (v / 1000).toFixed(1) + 's'; });
    if (DOM.collectionSelect) DOM.collectionSelect.addEventListener('change', onCollectionChange);
    if (DOM.settingsCollectionSelect) DOM.settingsCollectionSelect.addEventListener('change', onCollectionChange);
    if (DOM.newCollectionConfirm) DOM.newCollectionConfirm.addEventListener('click', confirmNewCollection);
    if (DOM.newCollectionCancel) DOM.newCollectionCancel.addEventListener('click', cancelNewCollection);
    if (DOM.newCollectionInput) DOM.newCollectionInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') confirmNewCollection(); else if (e.key === 'Escape') cancelNewCollection(); });
    if (DOM.pronAddBtn) DOM.pronAddBtn.addEventListener('click', function () { var word = (DOM.pronWordInput && DOM.pronWordInput.value.trim()); var repl = (DOM.pronReplacementInput && DOM.pronReplacementInput.value.trim()); if (!word || !repl) { toast('Enter both word and replacement.', 'warning'); return; } STATE.pronunciations[word] = repl; saveToStorage('pronunciations', STATE.pronunciations); renderPronunciationList(); if (DOM.pronWordInput) DOM.pronWordInput.value = ''; if (DOM.pronReplacementInput) DOM.pronReplacementInput.value = ''; toast('Pronunciation added.', 'success'); });
    if (DOM.newChatBtn) DOM.newChatBtn.addEventListener('click', startNewChat);
    if (DOM.clearKnowledgeBtn) DOM.clearKnowledgeBtn.addEventListener('click', function () {
        var col = getActiveCollection(); if (!confirm('Delete ALL vectors from collection "' + col + '"?')) return;
        fetch('/collections/' + col, { method: 'DELETE' }).then(function () {
            STATE.documents.ingested = []; saveDocumentsForCollection(col, []);
            STATE.lastIntentWasDocument = false; resetLastRetrievalState(); persistActiveCollectionRetrieval();
            renderDocumentList(); STATE.services.qdrant.collectionReady = false;
            return ensureCollection();
        }).then(function () { return fetchCollectionsAndPopulate(); }).then(function () { toast('Knowledge base cleared and collection recreated.', 'success'); }).catch(function (err) { toast('Failed to clear: ' + err.message, 'error'); });
    });
    if (DOM.groqKeyInput) DOM.groqKeyInput.addEventListener('change', function () { /* Backend manages keys now */ toast('API keys are managed via server .env file.', 'info'); });
    if (DOM.groqKeyToggle) DOM.groqKeyToggle.addEventListener('click', function () { if (!DOM.groqKeyInput) return; DOM.groqKeyInput.type = DOM.groqKeyInput.type === 'password' ? 'text' : 'password'; });
    
    // Model selects
    if (DOM.chatModelSelect) {
        DOM.chatModelSelect.addEventListener('change', function () {
            var val = this.value;
            if (!val) { STATE.llm.activeChatProvider = ''; STATE.llm.activeChatModel = ''; }
            else { var parts = val.split('|'); STATE.llm.activeChatProvider = parts[0]; STATE.llm.activeChatModel = parts[1]; }
            saveToStorage('active_chat_provider', STATE.llm.activeChatProvider);
            saveToStorage('active_chat_model', STATE.llm.activeChatModel);
        });
    }
    if (DOM.embedModelSelect) {
        DOM.embedModelSelect.addEventListener('change', function () {
            STATE.embeddings.activeModel = this.value;
            saveToStorage('active_embed_model', this.value);
            toast('Embedding model changed. Re-upload documents to take effect.', 'warning');
        });
    }

    document.addEventListener('keydown', function (e) {
        var tag = document.activeElement && document.activeElement.tagName; var inInput = (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT');
        if (e.key === ' ' && !inInput) { e.preventDefault(); toggleListening(); }
        if (e.key === 'Escape') { stopEverything(); closeSettingsPanel(); closeDocumentsPanel(); closeHistoryPanel(); }
        if (e.ctrlKey && !e.shiftKey && e.key === 'u') { e.preventDefault(); if (DOM.fileInput) DOM.fileInput.click(); }
        if (e.ctrlKey && e.shiftKey && e.key === 'H') { e.preventDefault(); if (DOM.handsfreeToggle) { DOM.handsfreeToggle.checked = !DOM.handsfreeToggle.checked; DOM.handsfreeToggle.dispatchEvent(new Event('change')); } }
        if (e.ctrlKey && e.key === 'h') { e.preventDefault(); STATE.ui.historyPanelOpen ? closeHistoryPanel() : openHistoryPanel(); }
        if (e.ctrlKey && e.key === ',') { e.preventDefault(); STATE.ui.settingsPanelOpen ? closeSettingsPanel() : openSettingsPanel(); }
    });
}


// ═══════════════════════════════════════════════════════════════
//  SECTION 18: INITIALIZATION ENTRY POINT
// ═══════════════════════════════════════════════════════════════



function init() {
    cacheDom(); loadSettings(); bindEvents(); NativeTTS.init(); PCMAudioPlayer.init(); startOrbAnimation();
    renderConversationToUi(); renderDocumentList();
    boot().catch(function (err) {
        console.error('Boot error:', err);
        addMessage('system', 'Initialization error: ' + err.message);
        setPhase('idle');
    });
}

document.addEventListener('DOMContentLoaded', init);

document.addEventListener('DOMContentLoaded', function () {
    var searchInput = document.getElementById('native-voice-search');
    if (searchInput) searchInput.addEventListener('input', function (e) { populateNativeVoiceDropdown(e.target.value); });
});
