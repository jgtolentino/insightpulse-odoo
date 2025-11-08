FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Copy skills (mounted volume in production)
COPY ../../skills /app/skills

# Create export directory
RUN mkdir -p /opt/insightpulse-odoo/exports/process-intel

ENV PORT=8090
ENV PYTHONUNBUFFERED=1

EXPOSE 8090

CMD ["python", "main.py"]
