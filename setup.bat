@echo off
setlocal EnableDelayedExpansion

echo Creating Conda environment...
call conda create --name karaoke_env python=3.10 -y

echo Activating Conda environment...
call conda activate karaoke_env

echo Checking for NVIDIA GPU...
where nvidia-smi >nul 2>nul
if %errorlevel% neq 0 (
    echo No NVIDIA GPU detected. Installing CPU-only PyTorch...
    call pip install torch torchvision torchaudio
    goto install_dependencies
)

echo GPU detected! Checking NVIDIA Driver version...
:: Remove "noheader" and use skip=1 to ignore the header line.
for /f "skip=1 tokens=* delims=" %%i in ('nvidia-smi --query-gpu=driver_version --format=csv') do (
    set "DRIVER_VERSION=%%i"
)

if "!DRIVER_VERSION!"=="" (
    echo Failed to detect driver version. Installing CPU-only PyTorch...
    set "CUDA_VERSION=CPU"
) else (
    :: Remove periods to form a comparable number (e.g. "571.96" -> "57196")
    set "DRIVER_VERSION_NUM=!DRIVER_VERSION!"
    set "DRIVER_VERSION_NUM=!DRIVER_VERSION_NUM:.=!"
    echo Detected NVIDIA Driver version: !DRIVER_VERSION!
    
    set "CUDA_VERSION=CPU"
    if !DRIVER_VERSION_NUM! GEQ 57000 (
        set "CUDA_VERSION=12.6"
    )
    if !DRIVER_VERSION_NUM! GEQ 55000 if !DRIVER_VERSION_NUM! LSS 57000 (
        set "CUDA_VERSION=12.4"
    )
    if !DRIVER_VERSION_NUM! GEQ 51500 if !DRIVER_VERSION_NUM! LSS 55000 (
        set "CUDA_VERSION=11.8"
    )
)

echo Detected CUDA version: !CUDA_VERSION!

:: Install the appropriate PyTorch version
if "!CUDA_VERSION!"=="12.6" (
    echo Installing PyTorch for CUDA 12.6...
    call pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
) else (
    if "!CUDA_VERSION!"=="12.4" (
        echo Installing PyTorch for CUDA 12.4...
        call pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    ) else (
        if "!CUDA_VERSION!"=="11.8" (
            echo Installing PyTorch for CUDA 11.8...
            call pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        ) else (
            echo CUDA version too low. Installing CPU-only PyTorch...
            call pip install torch torchvision torchaudio
        )
    )
)

:install_dependencies
echo Installing additional Conda dependencies...
call conda install -c conda-forge jupyterlab ipywidgets -y

echo Installing Pip dependencies...
call pip install python-dotenv
call pip install pyacoustid
call pip install demucs
call pip install colorlog
call pip install faster_whisper
call pip install deep_translator
call pip install langchain
call pip install langchain_google_genai
call pip install --upgrade gradio

echo Setup complete! Run "conda activate karaoke_env" to start using your environment.
pause
