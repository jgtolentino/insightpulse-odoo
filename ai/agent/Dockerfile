FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Run as non-root
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

ENTRYPOINT ["python", "-m", "ai.agent.main"]
