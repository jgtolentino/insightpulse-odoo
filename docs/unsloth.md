# Unsloth GPU Service

## Start
```bash
cp .env.example .env
make -f make/unsloth.mk unsloth-up
```

Jupyter: `http://localhost:8888` (password from `.env`)
API: `http://localhost:8000/health`

## Integrating with Odoo
1. Install addon **IP Unsloth Bridge** in your Odoo.
2. In *Settings → Technical → Unsloth*, set the base URL (defaults to `http://unsloth-api:8000`).
3. Open *Unsloth → Test Inference*, send a prompt, verify a response.

> Deploy Unsloth on a GPU host (NVIDIA drivers + Docker + nvidia-container-toolkit). DigitalOcean App Platform has no GPUs; use a **GPU Droplet** or any on-prem GPU box and point Odoo to its URL.
