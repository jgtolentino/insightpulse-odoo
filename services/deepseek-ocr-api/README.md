# DeepSeek-OCR Inference Service

FastAPI service for DeepSeek-OCR 3B model with LangChain integration.

## Features

- **DeepSeek-OCR 3B Model**: Multi-modal OCR with document understanding
- **LangChain Integration**: Document chunking and processing
- **Multiple Image Sizes**: Tiny (512x512), Small (640x640), Base (1024x1024), Large (1280x1280)
- **Supabase Integration**: Automatic result storage
- **FastAPI**: High-performance async API
- **Docker**: Containerized deployment

## API Endpoints

### Health Check
```bash
GET /health
```

### OCR Extraction
```bash
POST /v1/ocr
Content-Type: multipart/form-data

file: image file
output_format: "markdown" | "plain"
use_langchain: true | false
```

### Document Parsing (with LangChain)
```bash
POST /v1/parse
Content-Type: multipart/form-data

file: image file
```

## Deployment

### Local Docker
```bash
docker build -t deepseek-ocr:latest .
docker run -p 8000:8000 \
  -e MODEL_NAME=deepseek-ai/DeepSeek-OCR \
  -e TORCH_DEVICE=cpu \
  -e IMAGE_SIZE=base \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_SERVICE_ROLE_KEY=your-key \
  deepseek-ocr:latest
```

### Production (DigitalOcean Droplet)
```bash
# On OCR droplet (188.166.237.231)
cd /root
docker compose -f deepseek-ocr-docker-compose.yml up -d
```

## Environment Variables

- `MODEL_NAME`: HuggingFace model ID (default: deepseek-ai/DeepSeek-OCR)
- `TORCH_DEVICE`: cpu | cuda (default: cpu)
- `IMAGE_SIZE`: tiny | small | base | large (default: base)
- `PORT`: API port (default: 8000)
- `TRANSFORMERS_CACHE`: Model cache directory
- `HF_HOME`: HuggingFace home directory
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key

## Model Cache

Models are cached to `/models` volume (100GB) for faster loading:
- First run: Downloads ~3GB model files
- Subsequent runs: Loads from cache (< 30s startup)

## Usage Example

```python
import requests

# Upload image for OCR
with open("document.jpg", "rb") as f:
    response = requests.post(
        "http://ocr.insightpulseai.net:8100/v1/parse",
        files={"file": f}
    )

result = response.json()
print(result["text"])  # Extracted markdown text
print(result["langchain_chunks"])  # Text chunks for processing
```

## Performance

- **Startup**: ~2-3 minutes (first run), ~30s (cached)
- **OCR Speed**: ~2-5s per image (CPU)
- **Memory**: ~4GB RAM recommended
- **Disk**: ~3GB for model + cache
