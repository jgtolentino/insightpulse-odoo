-- Training Infrastructure Schema
-- Supports MCP training tools for BIR compliance, expense classification, etc.

-- ============================================================================
-- Training Datasets Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.training_datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Dataset metadata
  dataset_name TEXT NOT NULL,
  dataset_path TEXT NOT NULL,
  form_types TEXT[] NOT NULL,  -- ["1601C", "2550Q", "2307"]
  source TEXT NOT NULL,  -- "production", "validation_queue", "manual_upload"

  -- Statistics
  num_examples INT NOT NULL,
  avg_confidence FLOAT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  status TEXT DEFAULT 'ready' CHECK (status IN ('preparing', 'ready', 'training', 'archived'))
);

CREATE INDEX idx_training_datasets_status ON public.training_datasets(status, created_at DESC);
CREATE INDEX idx_training_datasets_form_types ON public.training_datasets USING GIN (form_types);

-- ============================================================================
-- Training Jobs Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.training_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Job identification
  job_id TEXT UNIQUE NOT NULL,
  dataset_path TEXT NOT NULL,
  config_template TEXT NOT NULL,
  model_output_dir TEXT NOT NULL,
  base_model TEXT NOT NULL,

  -- Process info
  pid INT,
  status TEXT DEFAULT 'running' CHECK (status IN ('queued', 'running', 'completed', 'failed')),

  -- Training config
  config JSONB NOT NULL,
  log_file TEXT,

  -- Timestamps
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_training_jobs_status ON public.training_jobs(status, started_at DESC);
CREATE INDEX idx_training_jobs_job_id ON public.training_jobs(job_id);

-- Trigger: Update timestamp
CREATE OR REPLACE FUNCTION update_training_jobs_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_training_jobs_timestamp
BEFORE UPDATE ON public.training_jobs
FOR EACH ROW
EXECUTE FUNCTION update_training_jobs_timestamp();

-- ============================================================================
-- Model Deployments Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.model_deployments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Model info
  model_name TEXT UNIQUE NOT NULL,
  model_path TEXT NOT NULL,
  container_id TEXT,

  -- Endpoints
  vllm_endpoint TEXT,
  litellm_gateway TEXT,

  -- Status
  status TEXT DEFAULT 'running' CHECK (status IN ('deploying', 'running', 'stopped', 'failed')),

  -- Timestamps
  deployed_at TIMESTAMP DEFAULT NOW(),
  stopped_at TIMESTAMP
);

CREATE INDEX idx_model_deployments_status ON public.model_deployments(status);
CREATE INDEX idx_model_deployments_name ON public.model_deployments(model_name);

-- ============================================================================
-- Model Evaluations Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.model_evaluations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Evaluation metadata
  model_name TEXT NOT NULL,
  eval_type TEXT NOT NULL,  -- "bir_compliance", "expense_accuracy", "finance_ssc"
  test_dataset TEXT NOT NULL,

  -- Results
  num_tests INT NOT NULL,
  avg_accuracy FLOAT NOT NULL,
  avg_f1_score FLOAT,
  avg_latency_ms FLOAT,

  -- Detailed results
  results JSONB NOT NULL,

  -- Timestamps
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_model_evaluations_model ON public.model_evaluations(model_name, timestamp DESC);
CREATE INDEX idx_model_evaluations_type ON public.model_evaluations(eval_type, timestamp DESC);

-- ============================================================================
-- Training Metrics Table (real-time progress tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.training_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Reference
  job_id TEXT NOT NULL,

  -- Metrics
  epoch INT,
  step INT,
  loss FLOAT,
  learning_rate FLOAT,
  grad_norm FLOAT,

  -- Timestamps
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_training_metrics_job ON public.training_metrics(job_id, timestamp DESC);

-- ============================================================================
-- Views
-- ============================================================================

-- Training Dashboard View
CREATE OR REPLACE VIEW public.training_dashboard AS
SELECT
  tj.job_id,
  tj.status,
  tj.started_at,
  tj.completed_at,
  EXTRACT(EPOCH FROM (COALESCE(tj.completed_at, NOW()) - tj.started_at)) / 60 AS duration_minutes,
  tj.config->>'num_epochs' AS total_epochs,
  COALESCE((
    SELECT MAX(epoch)
    FROM public.training_metrics tm
    WHERE tm.job_id = tj.job_id
  ), 0) AS current_epoch,
  COALESCE((
    SELECT MIN(loss)
    FROM public.training_metrics tm
    WHERE tm.job_id = tj.job_id
  ), 0) AS best_loss,
  td.num_examples AS training_examples,
  td.form_types
FROM public.training_jobs tj
LEFT JOIN public.training_datasets td ON tj.dataset_path = td.dataset_path
ORDER BY tj.started_at DESC;

-- Model Performance Leaderboard
CREATE OR REPLACE VIEW public.model_leaderboard AS
SELECT
  model_name,
  eval_type,
  COUNT(*) AS num_evaluations,
  AVG(avg_accuracy) AS avg_accuracy,
  AVG(avg_f1_score) AS avg_f1_score,
  AVG(avg_latency_ms) AS avg_latency_ms,
  MAX(timestamp) AS last_evaluated
FROM public.model_evaluations
GROUP BY model_name, eval_type
ORDER BY avg_f1_score DESC;

-- ============================================================================
-- Functions
-- ============================================================================

-- Get active training jobs
CREATE OR REPLACE FUNCTION public.get_active_training_jobs()
RETURNS TABLE (
  job_id TEXT,
  status TEXT,
  progress FLOAT,
  current_epoch INT,
  best_loss FLOAT,
  eta_minutes INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    tj.job_id,
    tj.status,
    COALESCE(
      (SELECT MAX(epoch) FROM training_metrics WHERE job_id = tj.job_id)::FLOAT
      / NULLIF((tj.config->>'num_epochs')::INT, 0),
      0.0
    ) AS progress,
    COALESCE((SELECT MAX(epoch) FROM training_metrics WHERE job_id = tj.job_id), 0) AS current_epoch,
    COALESCE((SELECT MIN(loss) FROM training_metrics WHERE job_id = tj.job_id), 0.0) AS best_loss,
    CASE
      WHEN tj.status = 'running' THEN
        CEIL(
          EXTRACT(EPOCH FROM (NOW() - tj.started_at)) / 60
          / NULLIF(COALESCE(
            (SELECT MAX(epoch) FROM training_metrics WHERE job_id = tj.job_id)::FLOAT
            / NULLIF((tj.config->>'num_epochs')::INT, 0),
            0.01
          ), 0)
          * (1.0 - COALESCE(
            (SELECT MAX(epoch) FROM training_metrics WHERE job_id = tj.job_id)::FLOAT
            / NULLIF((tj.config->>'num_epochs')::INT, 0),
            0.0
          ))
        )::INT
      ELSE 0
    END AS eta_minutes
  FROM public.training_jobs tj
  WHERE tj.status IN ('queued', 'running')
  ORDER BY tj.started_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Get model deployment status
CREATE OR REPLACE FUNCTION public.get_model_status(p_model_name TEXT)
RETURNS TABLE (
  model_name TEXT,
  status TEXT,
  vllm_endpoint TEXT,
  uptime_hours FLOAT,
  latest_accuracy FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    md.model_name,
    md.status,
    md.vllm_endpoint,
    EXTRACT(EPOCH FROM (NOW() - md.deployed_at)) / 3600 AS uptime_hours,
    (
      SELECT avg_accuracy
      FROM public.model_evaluations
      WHERE model_name = md.model_name
      ORDER BY timestamp DESC
      LIMIT 1
    ) AS latest_accuracy
  FROM public.model_deployments md
  WHERE md.model_name = p_model_name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Row-Level Security (RLS)
-- ============================================================================

ALTER TABLE public.training_datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_metrics ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can view training data
CREATE POLICY "Authenticated users can view training data"
ON public.training_datasets
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Authenticated users can view training jobs"
ON public.training_jobs
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Authenticated users can view deployments"
ON public.model_deployments
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Authenticated users can view evaluations"
ON public.model_evaluations
FOR SELECT
TO authenticated
USING (true);

-- Policy: Service role can modify all tables
CREATE POLICY "Service role full access - datasets"
ON public.training_datasets
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role full access - jobs"
ON public.training_jobs
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role full access - deployments"
ON public.model_deployments
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role full access - evaluations"
ON public.model_evaluations
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role full access - metrics"
ON public.training_metrics
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- ============================================================================
-- Sample Data
-- ============================================================================

-- Example training dataset
INSERT INTO public.training_datasets (
  dataset_name,
  dataset_path,
  form_types,
  source,
  num_examples,
  avg_confidence
) VALUES (
  'bir_1601C_2550Q_20250107',
  '/opt/insightpulse/training/datasets/bir_1601C_2550Q_20250107.jsonl',
  ARRAY['1601C', '2550Q'],
  'validation_queue',
  1250,
  0.92
);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE public.training_datasets IS
'Training datasets prepared from production OCR results and validated corrections.';

COMMENT ON TABLE public.training_jobs IS
'Axolotl fine-tuning jobs with real-time status tracking.';

COMMENT ON TABLE public.model_deployments IS
'vLLM model deployments registered in LiteLLM gateway.';

COMMENT ON TABLE public.model_evaluations IS
'Model evaluation results on test datasets (BIR compliance, expense accuracy, etc).';

COMMENT ON VIEW public.training_dashboard IS
'Real-time training dashboard with progress, loss, and ETA.';

COMMENT ON VIEW public.model_leaderboard IS
'Model performance leaderboard by accuracy and F1 score.';
