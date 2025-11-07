#!/usr/bin/env python3
"""
InsightPulse AI Training Hub - MCP Server Extension
Adds training orchestration tools to existing MCP server at mcp.insightpulseai.net

Architecture:
- Claude Max (your subscription) → MCP → Training stack
- No API costs - uses your Max subscription
- CLI bash scripts + cron for automation
- Integrates with PR #320 (Axolotl, vLLM, Unsloth, LiteLLM)

Tools:
1. prepare_bir_training_data - Extract & validate BIR forms
2. start_axolotl_training - Launch RTX 4090 optimized training
3. deploy_vllm_model - Serve fine-tuned models
4. run_model_evaluation - Validate against test sets
5. get_training_status - Monitor job progress
6. list_available_models - Show deployed models

Usage (from Claude Max):
- "Start BIR training with forms from this week"
- "Deploy the latest expense classification model"
- "Show me training metrics for bir-compliance model"
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import yaml
from mcp.server.fastmcp import FastMCP
from supabase import create_client, Client

# Initialize MCP server
mcp = FastMCP("insightpulse-training-hub")

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://spdtwktxdalcfigzeqrz.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service endpoints
OCR_API = os.getenv("OCR_API_URL", "http://ocr.insightpulseai.net")
POSTGRES_URL = os.getenv("POSTGRES_URL", "")

# Training paths
TRAINING_ROOT = Path("/opt/insightpulse/training")
DATASETS_DIR = TRAINING_ROOT / "datasets"
MODELS_DIR = TRAINING_ROOT / "models"
CONFIGS_DIR = TRAINING_ROOT / "configs"
LOGS_DIR = TRAINING_ROOT / "logs"

# Create directories
for dir_path in [DATASETS_DIR, MODELS_DIR, CONFIGS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Tool 1: BIR Training Data Preparation
# ============================================================================

@mcp.tool()
async def prepare_bir_training_data(
    form_types: List[str],  # ["1601C", "2550Q", "1702RT", "2307"]
    source: str = "production",  # "production", "validation_queue", "manual_upload"
    min_confidence: float = 0.85,
    output_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Prepare BIR form training data from PaddleOCR output.

    Pipeline:
    1. Fetch forms from ocr.insightpulseai.net or Supabase
    2. Validate against BIR schemas
    3. Generate Axolotl-compatible JSONL
    4. Store metadata in Supabase

    Args:
        form_types: BIR form types to include
        source: Data source (production OCR, validation queue, or manual)
        min_confidence: Minimum OCR confidence threshold
        output_name: Custom dataset name (default: auto-generated)

    Returns:
        {
            "status": "success",
            "dataset_path": "/opt/insightpulse/training/datasets/bir_1601C_20250107.jsonl",
            "num_examples": 1250,
            "form_types": ["1601C", "2550Q"],
            "avg_confidence": 0.92,
            "metadata_id": "uuid-..."
        }
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_name = output_name or f"bir_{'_'.join(form_types)}_{timestamp}"
    dataset_path = DATASETS_DIR / f"{dataset_name}.jsonl"

    training_examples = []

    # Fetch data based on source
    if source == "production":
        # Query Supabase for production OCR results
        response = supabase.table("ocr_results").select("*").in_(
            "form_type", form_types
        ).gte("confidence", min_confidence).execute()

        raw_forms = response.data

    elif source == "validation_queue":
        # Get validated corrections from human reviewers
        response = supabase.table("ocr_validation_queue").select("*").in_(
            "document_type", [f"BIR_FORM_{ft}" for ft in form_types]
        ).eq("status", "validated").execute()

        raw_forms = response.data

    else:  # manual_upload
        # Scan manual upload directory
        upload_dir = TRAINING_ROOT / "uploads" / "bir"
        raw_forms = []
        for form_type in form_types:
            type_dir = upload_dir / form_type
            if type_dir.exists():
                for json_file in type_dir.glob("*.json"):
                    with open(json_file) as f:
                        raw_forms.append(json.load(f))

    # Process each form into training format
    for form in raw_forms:
        # Extract fields
        form_type = form.get("form_type") or form.get("document_type", "").replace("BIR_FORM_", "")

        if source == "validation_queue":
            # Use validated (corrected) data
            extracted_data = form.get("validated_text", {})
            raw_text = form.get("extracted_text", {})
        else:
            extracted_data = form.get("structured_data", form.get("fields", {}))
            raw_text = form.get("raw_text", "")

        # Generate training example
        training_example = {
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a BIR compliance expert. Extract all required fields from Philippine BIR Form {form_type} with 100% accuracy. Return structured JSON only."
                },
                {
                    "role": "user",
                    "content": f"Extract all fields from this BIR Form {form_type}:\n\n{raw_text}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps(extracted_data, indent=2)
                }
            ],
            "metadata": {
                "form_type": form_type,
                "source": source,
                "confidence": form.get("confidence", form.get("overall_confidence", 1.0)),
                "timestamp": form.get("created_at", datetime.now().isoformat())
            }
        }

        training_examples.append(training_example)

    # Write to JSONL
    with open(dataset_path, 'w') as f:
        for example in training_examples:
            f.write(json.dumps(example) + '\n')

    # Calculate statistics
    avg_confidence = sum(ex["metadata"]["confidence"] for ex in training_examples) / len(training_examples) if training_examples else 0

    # Store metadata in Supabase
    metadata = {
        "dataset_name": dataset_name,
        "dataset_path": str(dataset_path),
        "form_types": form_types,
        "source": source,
        "num_examples": len(training_examples),
        "avg_confidence": avg_confidence,
        "created_at": datetime.now().isoformat(),
        "status": "ready"
    }

    metadata_response = supabase.table("training_datasets").insert(metadata).execute()
    metadata_id = metadata_response.data[0]["id"] if metadata_response.data else None

    return {
        "status": "success",
        "dataset_path": str(dataset_path),
        "num_examples": len(training_examples),
        "form_types": form_types,
        "avg_confidence": round(avg_confidence, 3),
        "metadata_id": metadata_id
    }


# ============================================================================
# Tool 2: Start Axolotl Training Job
# ============================================================================

@mcp.tool()
async def start_axolotl_training(
    dataset_path: str,
    config_template: str = "bir-llama-lora",  # Pre-configured templates
    model_output_name: str = "",
    base_model: str = "meta-llama/Llama-3.3-70B-Instruct",
    learning_rate: float = 2e-4,
    epochs: int = 3,
    batch_size: int = 4,
    lora_r: int = 32,
    lora_alpha: int = 64,
    gpu_memory_utilization: float = 0.95
) -> Dict[str, Any]:
    """
    Start Axolotl fine-tuning job with RTX 4090 optimization.

    Pre-configured templates:
    - bir-llama-lora: Llama 3.3 70B LoRA for BIR forms
    - expense-mistral-qlora: Mistral 7B QLoRA for expense categorization
    - finance-ssc-full: Full fine-tune for month-end closing
    - receipt-ocr-lora: SmolLM2 LoRA for receipt extraction

    Args:
        dataset_path: Path to training JSONL file
        config_template: Template config name
        model_output_name: Output model directory name
        base_model: HuggingFace model ID
        learning_rate: Learning rate
        epochs: Number of training epochs
        batch_size: Micro batch size per device
        lora_r: LoRA rank
        lora_alpha: LoRA alpha
        gpu_memory_utilization: GPU memory usage (0.0-1.0)

    Returns:
        {
            "status": "training_started",
            "job_id": "bir-compliance-20250107-153045",
            "pid": 12345,
            "config_path": "/opt/insightpulse/training/configs/job_12345.yml",
            "model_output_dir": "/opt/insightpulse/training/models/bir-compliance-20250107",
            "estimated_duration": "45 minutes",
            "tensorboard_url": "http://localhost:6006",
            "log_file": "/opt/insightpulse/training/logs/job_12345.log"
        }
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"{model_output_name or 'training'}_{timestamp}"
    model_output_dir = MODELS_DIR / (model_output_name or f"model_{timestamp}")
    config_path = CONFIGS_DIR / f"job_{job_id}.yml"
    log_file = LOGS_DIR / f"job_{job_id}.log"

    # Load template config
    template_path = CONFIGS_DIR / "templates" / f"{config_template}.yml"
    if template_path.exists():
        with open(template_path) as f:
            config = yaml.safe_load(f)
    else:
        # Default config
        config = {}

    # Merge runtime parameters
    config.update({
        "base_model": base_model,
        "datasets": [
            {
                "path": dataset_path,
                "type": "json",
                "conversation": "messages"
            }
        ],
        "output_dir": str(model_output_dir),

        # Training params
        "learning_rate": learning_rate,
        "num_epochs": epochs,
        "micro_batch_size": batch_size,
        "gradient_accumulation_steps": 4,
        "warmup_steps": 10,
        "eval_steps": 50,
        "save_steps": 100,
        "logging_steps": 10,

        # LoRA config
        "adapter": "lora",
        "lora_r": lora_r,
        "lora_alpha": lora_alpha,
        "lora_dropout": 0.05,
        "lora_target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],

        # Optimization (RTX 4090)
        "bf16": True,
        "fp16": False,
        "flash_attention": True,
        "sample_packing": True,
        "eval_sample_packing": False,
        "sequence_len": 4096,
        "load_in_4bit": False,  # Full precision on 4090
        "gradient_checkpointing": True,

        # Wandb logging
        "wandb_project": "insightpulse-training",
        "wandb_run_id": job_id,
        "wandb_log_model": "checkpoint"
    })

    # Save config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    # Launch training job (Docker Compose service)
    cmd = [
        "docker-compose", "-f", "/opt/insightpulse/docker-compose.training.yml",
        "exec", "-T", "axolotl",
        "accelerate", "launch", "-m", "axolotl.cli.train",
        str(config_path)
    ]

    # Start process in background
    with open(log_file, 'w') as log_f:
        process = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            cwd="/opt/insightpulse"
        )

    # Store job metadata in Supabase
    job_metadata = {
        "job_id": job_id,
        "dataset_path": dataset_path,
        "config_template": config_template,
        "model_output_dir": str(model_output_dir),
        "base_model": base_model,
        "status": "running",
        "pid": process.pid,
        "started_at": datetime.now().isoformat(),
        "config": config,
        "log_file": str(log_file)
    }

    supabase.table("training_jobs").insert(job_metadata).execute()

    # Estimate duration (rough heuristic: ~15 min per epoch for 70B LoRA)
    estimated_minutes = epochs * 15

    return {
        "status": "training_started",
        "job_id": job_id,
        "pid": process.pid,
        "config_path": str(config_path),
        "model_output_dir": str(model_output_dir),
        "estimated_duration": f"{estimated_minutes} minutes",
        "tensorboard_url": "http://localhost:6006",
        "log_file": str(log_file)
    }


# ============================================================================
# Tool 3: Deploy vLLM Model
# ============================================================================

@mcp.tool()
async def deploy_vllm_model(
    model_path: str,
    model_name: str,
    port: int = 8000,
    gpu_memory_utilization: float = 0.9,
    max_model_len: int = 4096,
    register_litellm: bool = True
) -> Dict[str, Any]:
    """
    Deploy fine-tuned model to vLLM inference server.
    Registers in LiteLLM gateway for OpenAI-compatible API.

    Args:
        model_path: Path to model directory (Axolotl output)
        model_name: Deployment name (e.g., "bir-compliance-prod")
        port: vLLM server port
        gpu_memory_utilization: GPU memory fraction (0.0-1.0)
        max_model_len: Maximum sequence length
        register_litellm: Add to LiteLLM gateway

    Returns:
        {
            "status": "deployed",
            "container_id": "abc123...",
            "model_name": "bir-compliance-prod",
            "vllm_endpoint": "http://localhost:8001/v1",
            "litellm_gateway": "http://localhost:4000/v1",
            "openai_compatible": true
        }
    """

    # Check if model exists
    model_dir = Path(model_path)
    if not model_dir.exists():
        raise ValueError(f"Model not found: {model_path}")

    # Stop existing container if running
    container_name = f"vllm-{model_name}"
    subprocess.run(
        ["docker", "stop", container_name],
        capture_output=True
    )
    subprocess.run(
        ["docker", "rm", container_name],
        capture_output=True
    )

    # Start vLLM server
    cmd = [
        "docker", "run", "-d",
        "--gpus", "all",
        "--name", container_name,
        "-p", f"{port}:8000",
        "-v", f"{model_path}:/model:ro",
        "--shm-size", "16g",
        "vllm/vllm-openai:latest",
        "--model", "/model",
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--max-model-len", str(max_model_len),
        "--dtype", "bfloat16",
        "--enable-chunked-prefill"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    container_id = result.stdout.strip()

    if result.returncode != 0:
        raise RuntimeError(f"vLLM deployment failed: {result.stderr}")

    # Wait for server to start (health check)
    vllm_endpoint = f"http://localhost:{port}/v1"
    max_retries = 30
    for i in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{vllm_endpoint}/models", timeout=5.0)
                if response.status_code == 200:
                    break
        except:
            pass
        await asyncio.sleep(2)
    else:
        raise RuntimeError("vLLM server failed to start within 60 seconds")

    # Register in LiteLLM gateway
    litellm_gateway = None
    if register_litellm:
        litellm_config_path = Path("/opt/insightpulse/litellm/config.yaml")

        # Load existing config
        if litellm_config_path.exists():
            with open(litellm_config_path) as f:
                litellm_config = yaml.safe_load(f) or {}
        else:
            litellm_config = {"model_list": []}

        # Add new model
        litellm_config["model_list"].append({
            "model_name": model_name,
            "litellm_params": {
                "model": "openai/vllm",
                "api_base": vllm_endpoint,
                "api_key": "dummy"
            }
        })

        # Save updated config
        with open(litellm_config_path, 'w') as f:
            yaml.dump(litellm_config, f, default_flow_style=False)

        # Restart LiteLLM gateway
        subprocess.run([
            "docker-compose", "-f", "/opt/insightpulse/docker-compose.training.yml",
            "restart", "litellm"
        ])

        litellm_gateway = "http://localhost:4000/v1"

    # Store deployment metadata
    deployment_metadata = {
        "model_name": model_name,
        "model_path": model_path,
        "container_id": container_id,
        "vllm_endpoint": vllm_endpoint,
        "litellm_gateway": litellm_gateway,
        "deployed_at": datetime.now().isoformat(),
        "status": "running"
    }

    supabase.table("model_deployments").insert(deployment_metadata).execute()

    return {
        "status": "deployed",
        "container_id": container_id,
        "model_name": model_name,
        "vllm_endpoint": vllm_endpoint,
        "litellm_gateway": litellm_gateway,
        "openai_compatible": True
    }


# ============================================================================
# Tool 4: Run Model Evaluation
# ============================================================================

@mcp.tool()
async def run_model_evaluation(
    model_endpoint: str,
    test_dataset: str,
    eval_type: str = "bir_compliance",  # "bir_compliance", "expense_accuracy", "finance_ssc"
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run evaluation suite and store results in Supabase.

    Evaluation types:
    - bir_compliance: BIR form field extraction accuracy
    - expense_accuracy: Expense categorization F1 score
    - finance_ssc: Month-end closing task completion

    Args:
        model_endpoint: Model API endpoint (vLLM or LiteLLM)
        test_dataset: Path to test JSONL file
        eval_type: Evaluation suite to run
        model_name: Model identifier for tracking

    Returns:
        {
            "eval_id": "uuid-...",
            "model_name": "bir-compliance-prod",
            "eval_type": "bir_compliance",
            "num_tests": 100,
            "accuracy": 0.94,
            "f1_score": 0.93,
            "avg_latency_ms": 245,
            "results_url": "https://supabase.co/dashboard/..."
        }
    """

    # Load test data
    test_dataset_path = Path(test_dataset)
    if not test_dataset_path.exists():
        raise ValueError(f"Test dataset not found: {test_dataset}")

    with open(test_dataset_path) as f:
        test_cases = [json.loads(line) for line in f]

    # Run evaluations
    results = []
    total_latency = 0

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, case in enumerate(test_cases):
            start_time = time.time()

            try:
                # Call model
                response = await client.post(
                    f"{model_endpoint}/chat/completions",
                    json={
                        "model": model_name or "vllm",
                        "messages": case["messages"][:-1],  # Exclude expected output
                        "max_tokens": 2048,
                        "temperature": 0.0  # Deterministic for evaluation
                    }
                )

                latency_ms = (time.time() - start_time) * 1000
                total_latency += latency_ms

                prediction = response.json()["choices"][0]["message"]["content"]
                expected = case["messages"][-1]["content"]

                # Calculate metrics based on eval type
                if eval_type == "bir_compliance":
                    metrics = calculate_bir_compliance_metrics(prediction, expected)
                elif eval_type == "expense_accuracy":
                    metrics = calculate_expense_accuracy_metrics(prediction, expected)
                elif eval_type == "finance_ssc":
                    metrics = calculate_finance_ssc_metrics(prediction, expected)
                else:
                    metrics = {"accuracy": 0.0}

                metrics["latency_ms"] = latency_ms
                metrics["test_case_id"] = i

                results.append(metrics)

            except Exception as e:
                results.append({
                    "test_case_id": i,
                    "error": str(e),
                    "accuracy": 0.0,
                    "latency_ms": 0
                })

    # Aggregate results
    avg_accuracy = sum(r.get("accuracy", 0) for r in results) / len(results)
    avg_f1 = sum(r.get("f1_score", 0) for r in results) / len(results)
    avg_latency = total_latency / len(results)

    # Store in Supabase
    eval_summary = {
        "model_name": model_name or "unknown",
        "eval_type": eval_type,
        "test_dataset": test_dataset,
        "timestamp": datetime.now().isoformat(),
        "num_tests": len(test_cases),
        "avg_accuracy": round(avg_accuracy, 4),
        "avg_f1_score": round(avg_f1, 4),
        "avg_latency_ms": round(avg_latency, 2),
        "results": results
    }

    eval_response = supabase.table("model_evaluations").insert(eval_summary).execute()
    eval_id = eval_response.data[0]["id"] if eval_response.data else None

    return {
        "eval_id": eval_id,
        "model_name": model_name or "unknown",
        "eval_type": eval_type,
        "num_tests": len(test_cases),
        "accuracy": round(avg_accuracy, 4),
        "f1_score": round(avg_f1, 4),
        "avg_latency_ms": round(avg_latency, 2),
        "results_url": f"{SUPABASE_URL}/dashboard/table/model_evaluations?id={eval_id}"
    }


# ============================================================================
# Tool 5: Get Training Status
# ============================================================================

@mcp.tool()
async def get_training_status(job_id: str) -> Dict[str, Any]:
    """
    Get real-time training job status from logs and Supabase.

    Args:
        job_id: Training job identifier

    Returns:
        {
            "job_id": "bir-compliance-20250107-153045",
            "status": "running",  # running, completed, failed
            "progress": 0.65,  # 0.0-1.0
            "current_epoch": 2,
            "total_epochs": 3,
            "loss": 0.234,
            "learning_rate": 0.0002,
            "eta_minutes": 15,
            "started_at": "2025-01-07T15:30:45Z",
            "last_update": "2025-01-07T15:45:12Z"
        }
    """

    # Query Supabase for job metadata
    response = supabase.table("training_jobs").select("*").eq("job_id", job_id).execute()

    if not response.data:
        raise ValueError(f"Training job not found: {job_id}")

    job_metadata = response.data[0]
    log_file = Path(job_metadata["log_file"])

    # Parse log file for latest metrics
    if log_file.exists():
        with open(log_file) as f:
            lines = f.readlines()

        # Extract latest training step (simplified parsing)
        latest_metrics = {
            "loss": None,
            "learning_rate": None,
            "current_epoch": None,
            "progress": 0.0
        }

        # Reverse search for latest metrics
        for line in reversed(lines[-100:]):  # Check last 100 lines
            if "loss" in line.lower():
                # Parse training log format (Axolotl specific)
                # Example: "{'loss': 0.234, 'learning_rate': 0.0002, 'epoch': 2.0}"
                try:
                    if "{" in line and "}" in line:
                        metrics_str = line[line.index("{"):line.rindex("}")+1]
                        metrics_dict = eval(metrics_str)
                        latest_metrics.update(metrics_dict)
                        break
                except:
                    pass

        # Calculate progress
        total_epochs = job_metadata["config"].get("num_epochs", 3)
        current_epoch = latest_metrics.get("epoch", latest_metrics.get("current_epoch", 0))
        progress = current_epoch / total_epochs if total_epochs > 0 else 0.0

        # Estimate ETA
        if progress > 0:
            elapsed_minutes = (datetime.now() - datetime.fromisoformat(job_metadata["started_at"])).total_seconds() / 60
            eta_minutes = int((elapsed_minutes / progress) - elapsed_minutes)
        else:
            eta_minutes = None
    else:
        latest_metrics = {}
        progress = 0.0
        eta_minutes = None

    # Determine status
    if job_metadata["status"] == "completed":
        status = "completed"
    elif job_metadata["status"] == "failed":
        status = "failed"
    else:
        # Check if process still running
        try:
            os.kill(job_metadata["pid"], 0)
            status = "running"
        except OSError:
            status = "failed"
            # Update in Supabase
            supabase.table("training_jobs").update({"status": "failed"}).eq("job_id", job_id).execute()

    return {
        "job_id": job_id,
        "status": status,
        "progress": round(progress, 3),
        "current_epoch": latest_metrics.get("epoch", latest_metrics.get("current_epoch")),
        "total_epochs": job_metadata["config"].get("num_epochs"),
        "loss": latest_metrics.get("loss"),
        "learning_rate": latest_metrics.get("learning_rate"),
        "eta_minutes": eta_minutes,
        "started_at": job_metadata["started_at"],
        "last_update": datetime.now().isoformat()
    }


# ============================================================================
# Tool 6: List Available Models
# ============================================================================

@mcp.tool()
async def list_available_models() -> Dict[str, Any]:
    """
    List all deployed models in vLLM + LiteLLM.

    Returns:
        {
            "models": [
                {
                    "name": "bir-compliance-prod",
                    "endpoint": "http://localhost:8001/v1",
                    "status": "running",
                    "deployed_at": "2025-01-07T15:30:45Z"
                },
                ...
            ],
            "total": 3
        }
    """

    # Query Supabase for deployed models
    response = supabase.table("model_deployments").select("*").eq("status", "running").execute()

    models = []
    for deployment in response.data:
        # Check if container still running
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", deployment["container_id"]],
                capture_output=True,
                text=True
            )
            is_running = result.stdout.strip() == "true"
        except:
            is_running = False

        if is_running:
            models.append({
                "name": deployment["model_name"],
                "endpoint": deployment["vllm_endpoint"],
                "litellm_gateway": deployment.get("litellm_gateway"),
                "status": "running",
                "deployed_at": deployment["deployed_at"]
            })

    return {
        "models": models,
        "total": len(models)
    }


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_bir_compliance_metrics(prediction: str, expected: str) -> Dict[str, float]:
    """
    Calculate BIR form extraction metrics.
    Compares predicted vs expected JSON fields.
    """
    try:
        pred_json = json.loads(prediction)
        exp_json = json.loads(expected)

        # Field-level accuracy
        total_fields = len(exp_json)
        correct_fields = sum(
            1 for key in exp_json
            if key in pred_json and str(pred_json[key]) == str(exp_json[key])
        )

        accuracy = correct_fields / total_fields if total_fields > 0 else 0.0

        # Precision/Recall for structured data
        predicted_fields = set(pred_json.keys())
        expected_fields = set(exp_json.keys())

        true_positives = len(predicted_fields & expected_fields)
        precision = true_positives / len(predicted_fields) if predicted_fields else 0.0
        recall = true_positives / len(expected_fields) if expected_fields else 0.0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }
    except:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1_score": 0.0}


def calculate_expense_accuracy_metrics(prediction: str, expected: str) -> Dict[str, float]:
    """Calculate expense categorization metrics"""
    # Simplified: exact match
    accuracy = 1.0 if prediction.strip().lower() == expected.strip().lower() else 0.0
    return {"accuracy": accuracy, "f1_score": accuracy}


def calculate_finance_ssc_metrics(prediction: str, expected: str) -> Dict[str, float]:
    """Calculate finance SSC task metrics"""
    # Placeholder: implement task-specific validation
    return {"accuracy": 0.5, "f1_score": 0.5}


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    # Start MCP server
    mcp.run()
