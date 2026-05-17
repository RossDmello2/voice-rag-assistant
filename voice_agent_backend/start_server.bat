@echo off
REM Voice Agent Backend — Start Script
REM Usage: double-click this file or run from command prompt

cd /d "%~dp0"

IF NOT EXIST ".env" (
    echo ERROR: .env file not found. Please copy ..\.env.example to .env and configure it.
    pause
    exit /b 1
)

set "NVIDIA_SITE=%APPDATA%\Python\Python312\site-packages\nvidia"
set "PATH=%NVIDIA_SITE%\cuda_runtime\bin;%NVIDIA_SITE%\cublas\bin;%NVIDIA_SITE%\cudnn\bin;%NVIDIA_SITE%\cuda_nvrtc\bin;%NVIDIA_SITE%\cufft\bin;%NVIDIA_SITE%\nvjitlink\bin;%PATH%"

echo Starting Voice Agent on http://localhost:8000 ...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
