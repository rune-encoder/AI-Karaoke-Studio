#!/bin/bash
set -e

# Create and activate the Conda environment
echo "Creating Conda environment..."
conda create --name karaoke_env python=3.10 -y

echo "Activating Conda environment..."

# Ensure the conda environment can be activated in this script
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate karaoke_env

# Detect the operating system
OS=$(uname)
echo "Detected OS: $OS"

# Default CUDA version setting is CPU-only
CUDA_VERSION="CPU"

if [ "$OS" == "Darwin" ]; then
    echo "macOS detected. Using CPU-only installation."
else
    # Assume Linux
    if ! command -v nvidia-smi &> /dev/null; then
        echo "No NVIDIA GPU detected. Installing CPU-only PyTorch..."
    else
        echo "GPU detected! Checking NVIDIA Driver version..."
        # Get the driver version; because --format=csv returns a header, skip it with tail.
        DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv | tail -n +2 | head -n 1)
        if [ -z "$DRIVER_VERSION" ]; then
            echo "Failed to get driver version. Installing CPU-only PyTorch..."
        else
            echo "Detected NVIDIA Driver version: $DRIVER_VERSION"
            # Remove the dot to compare as an integer (e.g., 571.96 becomes 57196)
            DRIVER_VERSION_NUM=$(echo "$DRIVER_VERSION" | tr -d '.')
            # Decide on CUDA version based on driver version
            if [ "$DRIVER_VERSION_NUM" -ge 57000 ]; then
                CUDA_VERSION="12.6"
            elif [ "$DRIVER_VERSION_NUM" -ge 55000 ]; then
                CUDA_VERSION="12.4"
            elif [ "$DRIVER_VERSION_NUM" -ge 51500 ]; then
                CUDA_VERSION="11.8"
            else
                CUDA_VERSION="CPU"
            fi
        fi
    fi
fi

echo "Detected CUDA version: $CUDA_VERSION"

# Install the appropriate PyTorch version
if [ "$CUDA_VERSION" == "12.6" ]; then
    echo "Installing PyTorch for CUDA 12.6..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
elif [ "$CUDA_VERSION" == "12.4" ]; then
    echo "Installing PyTorch for CUDA 12.4..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
elif [ "$CUDA_VERSION" == "11.8" ]; then
    echo "Installing PyTorch for CUDA 11.8..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "Installing CPU-only PyTorch..."
    pip install torch torchvision torchaudio
fi

# Install additional Conda dependencies
echo "Installing additional Conda dependencies..."
conda install -c conda-forge jupyterlab ipywidgets -y

# Install additional Pip dependencies
echo "Installing Pip dependencies..."
pip install python-dotenv
pip install pyacoustid
pip install demucs
pip install colorlog
pip install faster_whisper
pip install deep_translator
pip install langchain
pip install langchain_google_genai
pip install --upgrade gradio
pip install -U matplotlib

echo "Setup complete! Run 'conda activate karaoke_env' to start using your environment."
