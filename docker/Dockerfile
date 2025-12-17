# Use an official NVIDIA base image with CUDA support
FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04

# Set label for the docker image description
LABEL description="Docker image for xtts-api-server"

# Install required packages (avoid cache to reduce image size)
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    python3.11 python3.11-dev python3.11-venv python3.11-distutils python3.11-lib2to3 \
    portaudio19-dev libportaudio2 libasound2-dev libportaudiocpp0 \
    git make g++ ffmpeg vim build-essential cmake ninja-build wget sudo && \
    rm -rf /var/lib/apt/lists/*

# Set python3.11 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Create a virtual environment to avoid system package conflicts
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install required packages in virtual environment
RUN python3.11 -m pip install --upgrade pip setuptools wheel ninja virtualenv

# Copy the application source code to /app directory and change the workdir to /app
# COPY . /app
# WORKDIR /app

# Copy the application source code to /app directory

# Install Python dependencies
RUN python3.11 -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
RUN python3.11 -m pip install deepspeed
COPY . /app
WORKDIR /app
RUN python3.11 -m pip install -e .

# Expose the container ports
EXPOSE 8020

# Create workspace directory for persistent storage
VOLUME ["/workspace"]

# Run xtts_api_server when the container starts
CMD ["bash", "-c", "python3.11 -m xtts_api_server -hs 0.0.0.0 -p 8020 -d cuda -sf /workspace/speak -mf /workspace -ms api --listen --use-cache --deepspeed --streaming-mode-improve"]
