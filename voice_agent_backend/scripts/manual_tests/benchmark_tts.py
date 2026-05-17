import os
import sys
import time
import asyncio
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()

# Correct root discovery: the workspace root is where the .env file is.
WORKSPACE_ROOT = SCRIPT_PATH.parents[2]

sys.path.append(str(WORKSPACE_ROOT))

# Now we can import the DLL config logic
try:
    from app.core.onnx_runtime import configure_onnxruntime_gpu_environment
except ImportError as e:
    print(f"Import error: {e}. Trying to run without custom DLL config.")
    def configure_onnxruntime_gpu_environment(): pass

import onnxruntime as ort
from kokoro_onnx import Kokoro

# Derive model paths relative to the actual project structure.
MODEL_PATH = str(WORKSPACE_ROOT / "data" / "models" / "kokoro-v1.0.onnx")
VOICES_PATH = str(WORKSPACE_ROOT / "data" / "models" / "voices-v1.0.bin")

TEST_TEXT = "This is a performance benchmark to compare the speed of voice synthesis on the central processing unit versus the graphics processing unit. We are testing for hardware acceleration efficiency."

async def benchmark_hardware(hardware: str):
    print(f"\n--- Benchmarking {hardware.upper()} ---")
    
    # Configure environment for GPU
    if hardware == "gpu":
        print("Configuring GPU environment...")
        configure_onnxruntime_gpu_environment()

    providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if hardware == "gpu" else ["CPUExecutionProvider"]
    
    start_init = time.time()
    try:
        # Create a manual session to force hardware
        session = ort.InferenceSession(MODEL_PATH, providers=providers)
        # Verify provider
        actual_providers = session.get_providers()
        print(f"Available providers: {actual_providers}")
        actual_provider = actual_providers[0]
        
        if hardware == "gpu" and "CUDA" not in actual_provider:
            print("CRITICAL WARNING: Requested GPU but ONNX Runtime fell back to CPU.")
            # Even if it fell back, we can still run it as a 'second cpu test' or just fail
        
        kokoro = Kokoro.from_session(session, VOICES_PATH)
    except Exception as e:
        print(f"Failed to initialize {hardware}: {e}")
        return None
    init_time = time.time() - start_init
    print(f"Initialization: {init_time:.3f}s")

    # Warmup (important for GPU kernels)
    print("Warming up...")
    try:
        async for _ in kokoro.create_stream("Warmup text", voice="af_heart", speed=1.0):
            pass
    except Exception as e:
        print(f"Warmup failed: {e}")
        return None

    # Actual Benchmark
    print("Running timed test...")
    start_total = time.time()
    first_chunk_time = None
    chunk_count = 0
    total_samples = 0
    
    async for samples, _ in kokoro.create_stream(TEST_TEXT, voice="af_heart", speed=1.0):
        if first_chunk_time is None:
            first_chunk_time = time.time() - start_total
        chunk_count += 1
        total_samples += len(samples)
    
    total_time = time.time() - start_total
    
    print(f"Latency (First Chunk): {first_chunk_time:.3f}s")
    print(f"Total Synthesis Time:  {total_time:.3f}s")
    print(f"Chunks Generated:      {chunk_count}")
    print(f"Real-time factor:      { (total_samples/24000) / total_time:.2f}x")
    
    return {
        "hardware": hardware,
        "first_chunk": first_chunk_time,
        "total": total_time,
        "init": init_time,
        "provider": actual_provider
    }

async def main():
    # Verify files exist
    print(f"Checking for model at: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model file not found.")
        return
    if not os.path.exists(VOICES_PATH):
        print(f"ERROR: Voices file not found at {VOICES_PATH}")
        return

    results = []
    
    # Test CPU
    cpu_res = await benchmark_hardware("cpu")
    if cpu_res: results.append(cpu_res)
    
    # Test GPU
    gpu_res = await benchmark_hardware("gpu")
    if gpu_res: results.append(gpu_res)

    if len(results) >= 2:
        cpu_t = results[0]['total']
        gpu_t = results[1]['total']
        
        gpu_active = "CUDA" in results[1]['provider']
        
        if gpu_active and gpu_t > 0:
            speedup = cpu_t / gpu_t
            print(f"\n--- Final Comparison ---")
            print(f"CPU Total Time: {cpu_t:.3f}s")
            print(f"GPU Total Time: {gpu_t:.3f}s")
            print(f"GPU is {speedup:.2f}x faster than CPU.")
        elif not gpu_active:
            print(f"\n--- Result ---")
            print("Both tests used CPU. Check your CUDA/cuDNN installation.")
        else:
            print("\n--- Comparison failed due to zero time or error. ---")

if __name__ == "__main__":
    asyncio.run(main())
