-- Seed 001: Birth names sample data for Superset examples
-- Minimal sample dataset for dashboard binding

CREATE TABLE IF NOT EXISTS examples.birth_names (
  id SERIAL PRIMARY KEY,
  state TEXT,
  year INTEGER,
  gender TEXT,
  name TEXT,
  num INTEGER
);

-- Insert sample data (top 10 names from 2010)
INSERT INTO examples.birth_names (state, year, gender, name, num)
VALUES
  ('CA', 2010, 'F', 'Isabella', 3821),
  ('CA', 2010, 'F', 'Sophia', 3776),
  ('CA', 2010, 'F', 'Emma', 3046),
  ('CA', 2010, 'M', 'Jacob', 3692),
  ('CA', 2010, 'M', 'Ethan', 3371),
  ('CA', 2010, 'M', 'Daniel', 3314),
  ('NY', 2010, 'F', 'Isabella', 3108),
  ('NY', 2010, 'F', 'Sophia', 2956),
  ('NY', 2010, 'M', 'Jayden', 2844),
  ('NY', 2010, 'M', 'Jacob', 2740)
ON CONFLICT DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_birth_names_year ON examples.birth_names(year);
CREATE INDEX IF NOT EXISTS idx_birth_names_state ON examples.birth_names(state);
