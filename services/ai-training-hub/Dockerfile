FROM python:3.11-slim

# Install system dependencies for PaddleOCR and OpenCV
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy training scripts
COPY *.py ./

# Create directories for models and data
RUN mkdir -p /app/models /app/data

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TORCH_DEVICE=cpu

# Expose MLflow UI port
EXPOSE 5000

# Default command
CMD ["python", "-m", "mlflow", "ui", "--host", "0.0.0.0", "--port", "5000"]
