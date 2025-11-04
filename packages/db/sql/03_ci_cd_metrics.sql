-- CI/CD Metrics Tables

CREATE TABLE IF NOT EXISTS ops.workflow_runs (
    id SERIAL PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    status TEXT NOT NULL,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_workflow_runs_created_at ON ops.workflow_runs(created_at);
CREATE INDEX idx_workflow_runs_workflow_name ON ops.workflow_runs(workflow_name);

-- View for success rate metrics
CREATE OR REPLACE VIEW ops.workflow_success_rate AS
SELECT 
    workflow_name,
    COUNT(*) FILTER (WHERE status = 'success') * 100.0 / COUNT(*) AS success_rate,
    COUNT(*) AS total_runs,
    AVG(duration_seconds) FILTER (WHERE status = 'success') AS avg_duration
FROM ops.workflow_runs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY workflow_name;
