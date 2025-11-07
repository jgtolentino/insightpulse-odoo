FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN adduser --disabled-password --gecos "" app && apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && chown -R app:app /app
COPY . .
USER app
EXPOSE 8098
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8098"]
