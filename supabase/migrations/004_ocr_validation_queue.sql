-- OCR Validation Queue for Recursive Training Pipeline
-- Samsung-style self-improvement: collect low-confidence samples → human validation → retrain

-- ============================================================================
-- OCR Validation Queue Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.ocr_validation_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Original OCR result
  image_url TEXT NOT NULL,
  image_hash TEXT,  -- SHA256 hash to prevent duplicates
  ocr_provider TEXT DEFAULT 'paddleocr',  -- paddleocr, tesseract, etc.

  -- Extracted data (raw OCR output)
  extracted_text JSONB NOT NULL,  -- {fields: [{field_name, value, confidence, bbox}]}
  overall_confidence FLOAT NOT NULL,

  -- Document metadata
  document_type TEXT,  -- PHILIPPINE_RECEIPT, BIR_FORM_2307, etc.
  source TEXT,  -- api, upload, email, etc.

  -- Validation status
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'validated', 'rejected', 'retrained')),

  -- Human validation
  validated_text JSONB,  -- Corrected by human validator
  validated_by UUID REFERENCES auth.users(id),
  validated_at TIMESTAMP,
  validation_notes TEXT,

  -- Training metadata
  used_for_training BOOLEAN DEFAULT FALSE,
  training_batch_id UUID,
  training_date TIMESTAMP,

  -- Audit
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Query low-confidence samples
CREATE INDEX idx_ocr_validation_low_confidence
ON public.ocr_validation_queue(overall_confidence)
WHERE overall_confidence < 0.85 AND status = 'pending';

-- Query by status
CREATE INDEX idx_ocr_validation_status
ON public.ocr_validation_queue(status, created_at DESC);

-- Query by document type
CREATE INDEX idx_ocr_validation_doc_type
ON public.ocr_validation_queue(document_type);

-- Prevent duplicate submissions (same image)
CREATE UNIQUE INDEX idx_ocr_validation_unique_image
ON public.ocr_validation_queue(image_hash)
WHERE status NOT IN ('rejected');

-- GIN index for JSONB field searches
CREATE INDEX idx_ocr_validation_extracted_text
ON public.ocr_validation_queue USING GIN (extracted_text);

-- ============================================================================
-- Row-Level Security (RLS)
-- ============================================================================

ALTER TABLE public.ocr_validation_queue ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can view validation queue
CREATE POLICY "Authenticated users can view validation queue"
ON public.ocr_validation_queue
FOR SELECT
TO authenticated
USING (true);

-- Policy: Only validators can insert/update
CREATE POLICY "Validators can insert validation items"
ON public.ocr_validation_queue
FOR INSERT
TO authenticated
WITH CHECK (
  auth.jwt() ->> 'role' IN ('validator', 'admin')
  OR auth.jwt() ->> 'email' LIKE '%@insightpulseai.net'
);

CREATE POLICY "Validators can update validation items"
ON public.ocr_validation_queue
FOR UPDATE
TO authenticated
USING (
  auth.jwt() ->> 'role' IN ('validator', 'admin')
  OR auth.jwt() ->> 'email' LIKE '%@insightpulseai.net'
);

-- ============================================================================
-- Trigger: Update timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_ocr_validation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_ocr_validation_timestamp
BEFORE UPDATE ON public.ocr_validation_queue
FOR EACH ROW
EXECUTE FUNCTION update_ocr_validation_timestamp();

-- ============================================================================
-- View: Validation Dashboard Stats
-- ============================================================================

CREATE OR REPLACE VIEW public.ocr_validation_stats AS
SELECT
  date_trunc('day', created_at) AS date,
  document_type,
  COUNT(*) AS total_samples,
  COUNT(*) FILTER (WHERE status = 'pending') AS pending,
  COUNT(*) FILTER (WHERE status = 'validated') AS validated,
  COUNT(*) FILTER (WHERE status = 'rejected') AS rejected,
  COUNT(*) FILTER (WHERE used_for_training) AS used_for_training,
  AVG(overall_confidence) AS avg_confidence,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY overall_confidence) AS median_confidence
FROM public.ocr_validation_queue
GROUP BY date_trunc('day', created_at), document_type
ORDER BY date DESC;

-- ============================================================================
-- Function: Get samples for training batch
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_training_batch(
  batch_size INT DEFAULT 100,
  min_confidence FLOAT DEFAULT 0.0,
  max_confidence FLOAT DEFAULT 0.85
)
RETURNS TABLE (
  id UUID,
  image_url TEXT,
  extracted_text JSONB,
  validated_text JSONB,
  overall_confidence FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    q.id,
    q.image_url,
    q.extracted_text,
    q.validated_text,
    q.overall_confidence
  FROM public.ocr_validation_queue q
  WHERE
    q.status = 'validated'
    AND q.used_for_training = FALSE
    AND q.overall_confidence >= min_confidence
    AND q.overall_confidence <= max_confidence
    AND q.validated_text IS NOT NULL
  ORDER BY q.overall_confidence ASC  -- Prioritize lowest confidence (most learning potential)
  LIMIT batch_size;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Function: Mark samples as trained
-- ============================================================================

CREATE OR REPLACE FUNCTION public.mark_as_trained(
  sample_ids UUID[],
  batch_id UUID
)
RETURNS INT AS $$
DECLARE
  updated_count INT;
BEGIN
  UPDATE public.ocr_validation_queue
  SET
    used_for_training = TRUE,
    training_batch_id = batch_id,
    training_date = NOW(),
    status = 'retrained'
  WHERE id = ANY(sample_ids);

  GET DIAGNOSTICS updated_count = ROW_COUNT;
  RETURN updated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

INSERT INTO public.ocr_validation_queue (
  image_url,
  image_hash,
  extracted_text,
  overall_confidence,
  document_type,
  source
) VALUES
(
  'https://example.com/receipt_001.png',
  'sha256:abc123',
  '{"fields": [
    {"field_name": "merchant_name", "value": "SM SUPERMARKET", "confidence": 0.95, "bbox": [10, 10, 200, 30]},
    {"field_name": "tin", "value": "123-456-789-000", "confidence": 0.72, "bbox": [10, 40, 200, 60]},
    {"field_name": "total", "value": "1234.56", "confidence": 0.88, "bbox": [10, 300, 200, 320]}
  ]}'::JSONB,
  0.82,
  'PHILIPPINE_RECEIPT',
  'api'
);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE public.ocr_validation_queue IS
'Queue for human validation of low-confidence OCR results. Used for recursive training pipeline (Samsung-style self-improvement).';

COMMENT ON COLUMN public.ocr_validation_queue.overall_confidence IS
'Average confidence score across all extracted fields. Samples below 0.85 are sent to validation queue.';

COMMENT ON FUNCTION public.get_training_batch IS
'Retrieve validated samples for incremental training. Returns samples with lowest confidence first (highest learning potential).';

COMMENT ON VIEW public.ocr_validation_stats IS
'Dashboard view for validation queue metrics: pending samples, validation rate, confidence distribution.';
