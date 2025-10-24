FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create environment file template
COPY .env.example .env

# Expose port for the service
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
