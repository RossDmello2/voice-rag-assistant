import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def configure_onnxruntime_gpu_environment() -> None:
    """
    Expose NVIDIA Python package DLL folders so ONNX Runtime can load CUDA providers on Windows.
    Searches dynamically across potential site-packages locations.
    """
    import site
    
    # Potential search bases: User-site, Global-site, and current Env-site
    search_bases = []
    
    # 1. Standard site-packages (Global or Venv)
    for p in sys.path:
        if "site-packages" in p:
            search_bases.append(Path(p))
            
    # 2. User-specific site-packages
    try:
        if hasattr(site, "getusersitepackages"):
            user_site = site.getusersitepackages()
            if user_site:
                search_bases.append(Path(user_site))
    except Exception:
        pass

    # Unique sorted list of bases
    search_bases = sorted(list(set(search_bases)))
    found_any = False

    for base in search_bases:
        nvidia_base = base / "nvidia"
        if not nvidia_base.exists():
            continue
            
        # Standard sub-packages containing DLLs
        packages = ["cuda_runtime", "cublas", "cudnn", "cuda_nvrtc", "cufft", "nvjitlink"]
        
        for pkg in packages:
            bin_dir = nvidia_base / pkg / "bin"
            if not bin_dir.exists():
                continue
                
            bin_dir_str = str(bin_dir)
            
            # Add to Windows DLL search path
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(bin_dir_str)
                    logger.debug(f"Added DLL directory: {bin_dir_str}")
                except OSError:
                    pass
            
            # Add to environment PATH as fallback
            existing_path = os.environ.get("PATH", "")
            if bin_dir_str not in existing_path:
                os.environ["PATH"] = f"{bin_dir_str}{os.pathsep}{existing_path}"
                
            found_any = True

    if not found_any:
        logger.debug("No local NVIDIA wheels found in site-packages. Relying on system CUDA path.")
