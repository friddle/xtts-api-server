#!/bin/bash

echo "Checking GPU availability..."
if python3.10 -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    echo "GPU available, using CUDA and DeepSpeed"
    python3.10 -m xtts_api_server -hs 0.0.0.0 -p 8020 -d cuda -sf /workspace/speak -mf /workspace -ms api --listen --use-cache --deepspeed --streaming-mode-improve
else
    echo "GPU not available, using CPU (without DeepSpeed)"
    python3.10 -m xtts_api_server -hs 0.0.0.0 -p 8020 -d cpu -sf /workspace/speak -mf /workspace -ms api --listen --use-cache --streaming-mode-improve
fi
