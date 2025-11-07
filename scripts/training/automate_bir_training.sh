#!/bin/bash
# InsightPulse BIR Training Automation (replaces n8n)
# Cron: 0 2 * * * /opt/insightpulse/scripts/training/automate_bir_training.sh
# Runs daily at 2 AM, checks for new BIR forms, trains if needed

set -e

# Configuration
MCP_SERVER="http://mcp.insightpulseai.net"
SLACK_WEBHOOK="${SLACK_WEBHOOK_TRAINING:-}"
MIN_NEW_FORMS=50  # Minimum new forms to trigger training
LOG_FILE="/var/log/insightpulse/bir-training-$(date +%Y%m%d).log"

# Functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

notify_slack() {
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"🤖 BIR Training: $1\"}" \
            >/dev/null 2>&1
    fi
}

call_mcp_tool() {
    local tool_name=$1
    local params=$2

    curl -s -X POST "$MCP_SERVER/tools/$tool_name" \
        -H "Content-Type: application/json" \
        -d "$params"
}

# Main Pipeline
log "=== Starting BIR Training Automation ==="
notify_slack "Starting daily BIR training check..."

# Step 1: Prepare training data from production OCR + validation queue
log "Step 1: Preparing BIR training data..."

PREPARE_RESULT=$(call_mcp_tool "prepare_bir_training_data" '{
    "form_types": ["1601C", "2550Q", "1702RT", "2307"],
    "source": "validation_queue",
    "min_confidence": 0.85
}')

NUM_EXAMPLES=$(echo "$PREPARE_RESULT" | jq -r '.num_examples')
DATASET_PATH=$(echo "$PREPARE_RESULT" | jq -r '.dataset_path')
AVG_CONFIDENCE=$(echo "$PREPARE_RESULT" | jq -r '.avg_confidence')

log "✓ Prepared $NUM_EXAMPLES training examples (avg confidence: $AVG_CONFIDENCE)"

# Step 2: Check if we have enough new data to warrant training
if [ "$NUM_EXAMPLES" -lt "$MIN_NEW_FORMS" ]; then
    log "⏭️  Only $NUM_EXAMPLES new forms (min: $MIN_NEW_FORMS). Skipping training."
    notify_slack "Skipped training - only $NUM_EXAMPLES new forms (need $MIN_NEW_FORMS)"
    exit 0
fi

notify_slack "Found $NUM_EXAMPLES new validated forms. Starting training..."

# Step 3: Start Axolotl training job
log "Step 2: Starting Axolotl training job..."

TRAIN_RESULT=$(call_mcp_tool "start_axolotl_training" "{
    \"dataset_path\": \"$DATASET_PATH\",
    \"config_template\": \"bir-llama-lora\",
    \"model_output_name\": \"bir-compliance-$(date +%Y%m%d)\",
    \"base_model\": \"meta-llama/Llama-3.3-70B-Instruct\",
    \"learning_rate\": 0.0002,
    \"epochs\": 3,
    \"batch_size\": 4,
    \"lora_r\": 32,
    \"lora_alpha\": 64
}")

JOB_ID=$(echo "$TRAIN_RESULT" | jq -r '.job_id')
ESTIMATED_DURATION=$(echo "$TRAIN_RESULT" | jq -r '.estimated_duration')

log "✓ Training started: $JOB_ID (ETA: $ESTIMATED_DURATION)"
log "  TensorBoard: http://localhost:6006"
notify_slack "Training started: $JOB_ID (ETA: $ESTIMATED_DURATION)"

# Step 4: Monitor training progress
log "Step 3: Monitoring training progress..."

MAX_WAIT_MINUTES=120  # 2 hours max
CHECK_INTERVAL=60     # Check every minute
elapsed=0

while [ $elapsed -lt $((MAX_WAIT_MINUTES * 60)) ]; do
    sleep $CHECK_INTERVAL
    elapsed=$((elapsed + CHECK_INTERVAL))

    STATUS_RESULT=$(call_mcp_tool "get_training_status" "{\"job_id\": \"$JOB_ID\"}")

    STATUS=$(echo "$STATUS_RESULT" | jq -r '.status')
    PROGRESS=$(echo "$STATUS_RESULT" | jq -r '.progress')
    LOSS=$(echo "$STATUS_RESULT" | jq -r '.loss')
    ETA_MIN=$(echo "$STATUS_RESULT" | jq -r '.eta_minutes')

    log "  Status: $STATUS | Progress: $(echo "$PROGRESS * 100" | bc)% | Loss: $LOSS | ETA: ${ETA_MIN}min"

    if [ "$STATUS" = "completed" ]; then
        log "✓ Training completed successfully!"
        notify_slack "Training completed! Loss: $LOSS"
        break
    elif [ "$STATUS" = "failed" ]; then
        log "❌ Training failed. Check logs."
        notify_slack "❌ Training failed for $JOB_ID"
        exit 1
    fi
done

if [ "$STATUS" != "completed" ]; then
    log "⏰ Training timeout after ${MAX_WAIT_MINUTES} minutes"
    notify_slack "⏰ Training timeout for $JOB_ID"
    exit 1
fi

# Step 5: Deploy model to vLLM
log "Step 4: Deploying model to vLLM..."

MODEL_OUTPUT_DIR=$(echo "$TRAIN_RESULT" | jq -r '.model_output_dir')

DEPLOY_RESULT=$(call_mcp_tool "deploy_vllm_model" "{
    \"model_path\": \"$MODEL_OUTPUT_DIR\",
    \"model_name\": \"bir-compliance-prod\",
    \"port\": 8001,
    \"gpu_memory_utilization\": 0.9,
    \"register_litellm\": true
}")

CONTAINER_ID=$(echo "$DEPLOY_RESULT" | jq -r '.container_id')
VLLM_ENDPOINT=$(echo "$DEPLOY_RESULT" | jq -r '.vllm_endpoint')

log "✓ Model deployed: $CONTAINER_ID"
log "  Endpoint: $VLLM_ENDPOINT"
notify_slack "Model deployed: $VLLM_ENDPOINT"

# Step 6: Run evaluation on test set
log "Step 5: Running model evaluation..."

EVAL_RESULT=$(call_mcp_tool "run_model_evaluation" "{
    \"model_endpoint\": \"$VLLM_ENDPOINT\",
    \"test_dataset\": \"/opt/insightpulse/training/datasets/bir-test.jsonl\",
    \"eval_type\": \"bir_compliance\",
    \"model_name\": \"bir-compliance-prod\"
}")

ACCURACY=$(echo "$EVAL_RESULT" | jq -r '.accuracy')
F1_SCORE=$(echo "$EVAL_RESULT" | jq -r '.f1_score')
AVG_LATENCY=$(echo "$EVAL_RESULT" | jq -r '.avg_latency_ms')

log "✓ Evaluation complete:"
log "  Accuracy: $(echo "$ACCURACY * 100" | bc)%"
log "  F1 Score: $(echo "$F1_SCORE * 100" | bc)%"
log "  Latency: ${AVG_LATENCY}ms"

# Step 7: Notify stakeholders
notify_slack "✅ BIR Training Complete!
• Model: bir-compliance-$(date +%Y%m%d)
• Accuracy: $(echo "$ACCURACY * 100" | bc)%
• F1 Score: $(echo "$F1_SCORE * 100" | bc)%
• Latency: ${AVG_LATENCY}ms
• Endpoint: $VLLM_ENDPOINT"

log "=== BIR Training Pipeline Complete ==="
