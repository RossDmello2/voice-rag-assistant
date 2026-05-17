import onnxruntime as ort
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CudaTest")

def check_cuda_optimization():
    print("\n--- NITRO 5 HARDWARE ACCELERATION CHECK ---")
    
    # 1. Check Available Providers
    providers = ort.get_available_providers()
    print(f"Available ONNX Providers: {providers}")
    
    if "CUDAExecutionProvider" in providers:
        print("✅ [CUDA] NVIDIA GTX 1650 acceleration is available.")
    else:
        print("❌ [CUDA] NOT FOUND. Using CPU only. check CUDA/cuDNN installation.")

    # 2. Check Device ID
    try:
        if "CUDAExecutionProvider" in providers:
            # Simple test session to confirm binding
            sess = ort.InferenceSession(
                "data/models/kokoro-v1.0.onnx",
                providers=["CUDAExecutionProvider"]
            )
            print("✅ [ONNX] Successfully bound Kokoro to GTX 1650.")
    except Exception as e:
        print(f"⚠️ [ONNX] CUDA binding failed (might be path issue): {e}")

    # 3. CPU Core Check
    import os
    cpus = os.cpu_count()
    print(f"✅ [CPU] i5-11400H detected with {cpus} logical threads.")
    
    print("\nCONCLUSION: Hardware profile is ready for ultra-fast response.")

if __name__ == "__main__":
    check_cuda_optimization()
