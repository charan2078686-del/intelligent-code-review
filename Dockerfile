FROM rocm/pytorch:latest

WORKDIR /app

# Ensure non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# Update system packages and install necessary runtimes
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crucial: Use --no-deps to avoid replacing the ROCm PyTorch build with a CUDA build
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-deps -U \
    transformers \
    tokenizers \
    safetensors && \
    pip install --no-cache-dir \
    pandas \
    pillow

# Copy application files
COPY server.py /app/server.py
COPY app.py /app/app.py

# Create directory for output results
RUN mkdir -p /app/output

# Start the background daemon when the container starts, then keep container alive
CMD python3 /app/server.py & tail -f /dev/null
