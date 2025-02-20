FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04 AS base

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install --no-install-recommends -y \
    tzdata \
    software-properties-common \
    curl \
    jq \
    build-essential \
    python3.10 \
    python3-pip \
    git \
    ffmpeg \
    libchromaprint-tools \
    vim \
    bzip2 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-c"]

RUN curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o ~/miniconda.sh && \
  bash ~/miniconda.sh -b -p /opt/conda && \
  rm ~/miniconda.sh

ENV PATH=/opt/conda/bin:$PATH

RUN conda create --name karaoke_env python=3.10 -y && conda init bash

FROM base AS download

RUN curl -L https://huggingface.co/Systran/faster-whisper-large-v2/resolve/main/model.bin?download=true --create-dirs -o /root/.cache/huggingface/hub/models--Systran--faster-whisper-large-v2/blobs/bf2a9746382e1aa7ffff6b3a0d137ed9edbd9670c3b87e5d35f5e85e70d0333a
RUN curl -L https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/04573f0d-f3cf25b2.th --create-dirs -o /root/.cache/torch/hub/checkpoints/04573f0d-f3cf25b2.th
RUN curl -L https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/92cfc3b6-ef3bcb9c.th --create-dirs -o /root/.cache/torch/hub/checkpoints/92cfc3b6-ef3bcb9c.th
RUN curl -L https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/d12395a8-e57c48e6.th --create-dirs -o /root/.cache/torch/hub/checkpoints/d12395a8-e57c48e6.th
RUN curl -L https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/f7e0c4bc-ba3fe64a.th --create-dirs -o /root/.cache/torch/hub/checkpoints/f7e0c4bc-ba3fe64a.th

RUN source activate && conda activate karaoke_env && \
  pip download torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

RUN source activate && conda activate karaoke_env && \
  pip download \
    python-dotenv \
    pyacoustid \
    demucs \
    colorlog \
    faster_whisper \
    deep_translator \
    langchain \
    langchain_google_genai \
    gradio \
    colorama

RUN source activate && conda activate karaoke_env && \
  conda install --download-only -c conda-forge jupyterlab ipywidgets pip -y

FROM download AS install

RUN source activate && conda activate karaoke_env && \
  conda config --append channels conda-forge && \
  conda config --append channels nvidia && \
  conda config --append channels pytorch && \
  conda install -c conda-forge jupyterlab ipywidgets pip -y && \
  pip install --upgrade \
    python-dotenv \
    pyacoustid \
    demucs \
    colorlog \
    faster_whisper \
    deep_translator \
    langchain \
    langchain_google_genai \
    gradio \
    colorama && \
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 && \
  pip cache purge && \
  conda clean -a && \
  conda info && \
  rm -f /*.whl /*.tar.gz

ENV PYTHONPATH=/app \
  PYTHONUNBUFFERED=1 \
  GRADIO_ALLOW_FLAGGING=never \
  GRADIO_NUM_PORTS=1 \
  GRADIO_ANALYTICS_ENABLED=False \
  GRADIO_SERVER_NAME=0.0.0.0 \
  GRADIO_THEME=huggingface \
  SYSTEM=spaces \
  NVIDIA_DRIVER_CAPABILITIES=all \
  NVIDIA_VISIBLE_DEVICES=all

FROM install AS publish

WORKDIR /app
RUN echo '' > ./requirements.txt
COPY app.py LICENSE README.md ./
COPY interface ./interface
COPY modules ./modules

EXPOSE 7860
CMD source activate && conda activate karaoke_env && python3 app.py
