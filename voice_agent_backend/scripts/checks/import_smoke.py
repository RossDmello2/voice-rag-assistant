"""Quick import test for all modules — cross-platform safe."""
import sys
import os
from pathlib import Path

# B-02 FIX: was hardcoded Windows absolute path — now uses script location
BACKEND_ROOT = Path(__file__).resolve().parents[2]
os.chdir(BACKEND_ROOT)
sys.path.insert(0, str(BACKEND_ROOT))

# Pre-set SECRET_KEY so Settings() doesn't fail when .env isn't auto-discovered
os.environ.setdefault("SECRET_KEY", "test_secret_key_min_32_chars_long_for_testing!!")

# B-06 FIX: track total test count properly instead of len(errors)+9 offset
total = 0
errors = []

def test(name, fn):
    global total
    total += 1
    try:
        fn()
        print(f"  OK  {name}")
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        errors.append((name, e))

# 1. Graph state
test("graph_state",   lambda: __import__("app.core.graph_state",  fromlist=["VoiceAgentState", "STAGE_LABELS"]))

# 2. Config
test("config",        lambda: __import__("app.core.config",        fromlist=["settings"]))

# 3. Schemas
test("schemas",       lambda: __import__("app.models.schemas",     fromlist=["ChatStreamRequest", "InterruptRequest"]))

# 4. Correlator
test("correlator",    lambda: __import__("app.core.correlator",    fromlist=["correlate_query"]))

# 5. Individual nodes
for node in [
    "translate_input", "check_interrupt", "classify_intent", "retrieve_context",
    "check_confidence", "generate_response", "synthesize_speech", "update_context",
    "handle_early_exit",
]:
    test(f"nodes/{node}", lambda n=node: __import__(f"app.core.nodes.{n}", fromlist=[""]))

# 6. Voice graph (lazy — should NOT crash even without full deps)
test("voice_graph",   lambda: __import__("app.core.voice_graph",   fromlist=["compiled_graph", "get_compiled_graph"]))

# 7. Speech service
test("speech_service",lambda: __import__("app.services.speech_service", fromlist=["speech_service"]))

# 8. Chat routes
test("chat_routes",   lambda: __import__("app.api.routes.chat",    fromlist=["router"]))

# 9. Auth routes
test("auth_routes",   lambda: __import__("app.api.routes.auth",    fromlist=["router"]))

# 10. Collections routes
test("collections_routes", lambda: __import__("app.api.routes.collections", fromlist=["router"]))

# 11. Ingest routes
test("ingest_routes", lambda: __import__("app.api.routes.ingest",  fromlist=["router"]))

# 12. Health routes
test("health_routes", lambda: __import__("app.api.routes.health",  fromlist=["router"]))

print(f"\n{'='*50}")
if errors:
    print(f"FAILURES: {len(errors)}/{total}")
    for name, err in errors:
        print(f"  - {name}: {err}")
    sys.exit(1)
else:
    print(f"ALL {total} IMPORTS PASSED")
