-- Receipts table with Row Level Security (RLS)
-- This table stores metadata about uploaded receipts
-- Actual files are stored in Supabase Storage with signed URLs

CREATE TABLE IF NOT EXISTS public.receipts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  file_name TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  file_size INTEGER NOT NULL,
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  odoo_expense_id INTEGER,
  error_message TEXT,
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_receipts_user_id ON public.receipts(user_id);
CREATE INDEX IF NOT EXISTS idx_receipts_status ON public.receipts(status);
CREATE INDEX IF NOT EXISTS idx_receipts_uploaded_at ON public.receipts(uploaded_at DESC);

-- Enable Row Level Security
ALTER TABLE public.receipts ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own receipts
CREATE POLICY "Users can view own receipts"
ON public.receipts
FOR SELECT
USING (auth.uid() = user_id);

-- RLS Policy: Users can insert their own receipts
CREATE POLICY "Users can insert own receipts"
ON public.receipts
FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can update their own receipts
CREATE POLICY "Users can update own receipts"
ON public.receipts
FOR UPDATE
USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE ON public.receipts TO authenticated;
GRANT USAGE ON SEQUENCE receipts_id_seq TO authenticated;

-- Create storage bucket for receipts (private, RLS enforced)
INSERT INTO storage.buckets (id, name, public)
VALUES ('receipts', 'receipts', false)
ON CONFLICT (id) DO NOTHING;

-- Storage RLS Policy: Users can upload to their own folder
CREATE POLICY "Users can upload own receipts"
ON storage.objects
FOR INSERT
WITH CHECK (
  bucket_id = 'receipts'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Storage RLS Policy: Users can view their own receipts
CREATE POLICY "Users can view own receipts"
ON storage.objects
FOR SELECT
USING (
  bucket_id = 'receipts'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Storage RLS Policy: Users can delete their own receipts
CREATE POLICY "Users can delete own receipts"
ON storage.objects
FOR DELETE
USING (
  bucket_id = 'receipts'
  AND auth.uid()::text = (storage.foldername(name))[1]
);
