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
    python3.10 python3.10-dev python3.10-venv python3.10-distutils python3.10-lib2to3 \
    portaudio19-dev libportaudio2 libasound2-dev libportaudiocpp0 \
    git make g++ ffmpeg vim build-essential cmake ninja-build wget sudo && \
    rm -rf /var/lib/apt/lists/*

# Set python3.10 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Create a virtual environment to avoid system package conflicts
RUN python3.10 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install required packages in virtual environment
RUN python3.10 -m pip install --upgrade pip setuptools wheel ninja virtualenv

# Copy requirements.txt first to leverage Docker layer caching
COPY requirements.txt /app/requirements.txt
WORKDIR /app

# Install Python dependencies from requirements.txt
RUN python3.10 -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
RUN python3.10 -m pip install deepspeed
RUN python3.10 -m pip install 'coqui-tts[languages]==0.24.1' 'transformers==4.36.2' --no-deps
RUN python3.10 -m pip install typing-extensions dataclasses
RUN python3.10 -m pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app
RUN python3.10 -m pip install -e .

# Copy the startup script
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose the container ports
EXPOSE 8020
# Create workspace directory for persistent storage
VOLUME ["/workspace"]

# Run xtts_api_server when the container starts
CMD ["/app/start.sh"]
