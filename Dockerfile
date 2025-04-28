# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .

# Install system dependencies for cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install python-jose
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir python-jose[cryptography]==3.3.0

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify python-jose installation
RUN python -c "import jose; print('python-jose installed:', jose.__version__)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]