# Use an official NVIDIA base image with CUDA support
FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04

# Set label for the docker image description
LABEL description="Docker image for xtts-api-server"

# Install required packages (avoid cache to reduce image size)
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3-dev portaudio19-dev libportaudio2 libasound2-dev libportaudiocpp0 \
    git python3 python3-pip make g++ ffmpeg vim build-essential cmake ninja-build wget sudo && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install virtualenv
RUN python3 -m pip install --upgrade pip setuptools wheel ninja virtualenv

# Copy the application source code to /app directory and change the workdir to /app
# COPY . /app
# WORKDIR /app

# Install Python dependencies
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128 --break-system-packages
RUN pip install deepspeed --break-system-packages
RUN pip install xtts-api-server --break-system-packages

# Expose the container ports
EXPOSE 8020

# Run xtts_api_server when the container starts
CMD ["bash", "-c", "python3 -m xtts_api_server -hs 0.0.0.0 -p 8020 -d cuda -sf /workspace/speak -mf /workspace -ms api --listen --use-cache --deepspeed --streaming-mode-improve"]
