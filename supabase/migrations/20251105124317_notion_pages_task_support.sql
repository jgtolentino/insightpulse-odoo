-- Migration: Add task-specific columns to notion_pages table
-- Date: 2025-11-05
-- Purpose: Support Notion BIR task management with multiple assignees

-- 1. Create notion_pages table if not exists
CREATE TABLE IF NOT EXISTS notion_pages (
  id text PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- 2. Add columns to support tasks and metadata
ALTER TABLE notion_pages
  ADD COLUMN IF NOT EXISTS is_task boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS title text,
  ADD COLUMN IF NOT EXISTS status text,
  ADD COLUMN IF NOT EXISTS priority smallint,
  ADD COLUMN IF NOT EXISTS due_at timestamptz,
  ADD COLUMN IF NOT EXISTS assignees uuid[] DEFAULT '{}'::uuid[],
  ADD COLUMN IF NOT EXISTS notion_page_id text,
  ADD COLUMN IF NOT EXISTS external_metadata jsonb DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS updated_by uuid;

-- 3. Indexes for common lookups and RLS performance
CREATE INDEX IF NOT EXISTS idx_notion_pages_is_task ON notion_pages(is_task);
CREATE INDEX IF NOT EXISTS idx_notion_pages_status ON notion_pages(status);
CREATE INDEX IF NOT EXISTS idx_notion_pages_due_at ON notion_pages(due_at);
CREATE INDEX IF NOT EXISTS idx_notion_pages_assignees ON notion_pages USING GIN (assignees);
CREATE INDEX IF NOT EXISTS idx_notion_pages_notion_page_id ON notion_pages(notion_page_id);

-- 4. Computed column via view (is_overdue)
CREATE OR REPLACE VIEW notion_pages_with_flags AS
SELECT
  np.*,
  (np.is_task AND np.due_at IS NOT NULL AND np.due_at < now()) AS is_overdue
FROM notion_pages np;

-- 5. Helper function to upsert a page (used by Edge Function via RPC)
CREATE OR REPLACE FUNCTION upsert_notion_page(
  p_notion_page_id text,
  p_title text,
  p_is_task boolean,
  p_status text,
  p_priority smallint,
  p_due_at timestamptz,
  p_assignees uuid[],
  p_external_metadata jsonb,
  p_updated_by uuid
) RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO notion_pages (
    notion_page_id, title, is_task, status, priority, due_at, assignees, external_metadata, updated_by, created_at, updated_at
  )
  VALUES (
    p_notion_page_id, p_title, p_is_task, p_status, p_priority, p_due_at, p_assignees, p_external_metadata, p_updated_by, now(), now()
  )
  ON CONFLICT (notion_page_id) DO UPDATE
  SET
    title = EXCLUDED.title,
    is_task = EXCLUDED.is_task,
    status = EXCLUDED.status,
    priority = EXCLUDED.priority,
    due_at = EXCLUDED.due_at,
    assignees = EXCLUDED.assignees,
    external_metadata = EXCLUDED.external_metadata,
    updated_by = EXCLUDED.updated_by,
    updated_at = now();
END;
$$;

-- 6. Grant execute to authenticated users
GRANT EXECUTE ON FUNCTION upsert_notion_page(text, text, boolean, text, smallint, timestamptz, uuid[], jsonb, uuid) TO authenticated;

-- 7. Comment for documentation
COMMENT ON TABLE notion_pages IS 'Stores synchronized Notion pages and tasks with support for multiple assignees';
COMMENT ON FUNCTION upsert_notion_page IS 'Upserts a Notion page/task with full metadata - called by notion-edge Edge Function';
