import inspect
try:
    from kokoro_onnx import Kokoro
    print(f"Kokoro.__init__ signature: {inspect.signature(Kokoro.__init__)}")
except ImportError:
    print("kokoro_onnx not installed")
except Exception as e:
    print(f"Error: {e}")
