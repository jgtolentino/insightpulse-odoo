# Skillsmith - Proposed Skills

This directory contains auto-generated skill candidates from the Skillsmith error mining system.

## What is Skillsmith?

Skillsmith automatically mines error patterns from production logs and generates skill candidates that can either:
- **Prevent** known errors (guardrails)
- **Auto-fix** known issues (fixers)

## Workflow

1. **Mining**: Every 6 hours, Skillsmith mines `error_signatures` from the last 30 days
2. **Generation**: Top error patterns are converted to skill YAML files
3. **Proposal**: Skills are placed here and a PR is created
4. **Review**: You review the proposals in the PR
5. **Approval**: Move approved skills to `skills/` directory
6. **Deployment**: Run `make retrain` to activate

## File Naming Convention

- `GR-ABCD1234_*.yaml` - Guardrail skills (prevent errors)
- `FX-ABCD1234_*.yaml` - Fixer skills (auto-patch issues)

The 8-character hex code is the first 8 chars of the error fingerprint.

## Approval Process

### For Guardrails

1. Review the pattern matching in the YAML
2. Verify it won't cause false positives
3. Test in sandbox if uncertain
4. Move to `skills/` directory
5. Update `status: approved` in the YAML
6. Run `make retrain`

```bash
# Example
mv skills/proposed/GR-ABCD1234_keyerror-in-sale.yaml skills/
sed -i 's/status: proposed/status: approved/' skills/GR-ABCD1234_keyerror-in-sale.yaml
make retrain
```

### For Fixers

1. Review the error pattern
2. **Implement the autopatch script** (see TODO in YAML)
3. Test the autopatch in sandbox
4. Verify unit tests pass
5. Move to `skills/` directory
6. Update `status: approved` in the YAML
7. Run `make retrain`

```bash
# Example
# 1. Implement autopatch
cat > autopatches/fx-abcd1234.py <<'PY'
def apply(repo_dir: str) -> bool:
    # Implement safe patch logic
    return True
PY

# 2. Test
pytest tests/test_autopatches.py::test_fx_abcd1234

# 3. Approve
mv skills/proposed/FX-ABCD1234_*.yaml skills/
sed -i 's/status: proposed/status: approved/' skills/FX-*.yaml
sed -i 's/dry_run: true/dry_run: false/' skills/FX-*.yaml
make retrain
```

## Configuration

Adjust mining thresholds in `.github/workflows/skillsmith.yml`:

```yaml
inputs:
  min_hits:
    default: '2'    # Minimum occurrences in 7 days
  top_n:
    default: '50'   # Maximum candidates per run
```

## Metadata

Each skill file contains:

- `fingerprint`: Stable error signature (UUID)
- `hits_7d`: Occurrences in last 7 days
- `hits_30d`: Occurrences in last 30 days
- `impact_score`: Weighted score (7d × 0.7 + 30d × 0.3)
- `generated_at`: ISO timestamp

## Manual Mining

You can run mining manually:

```bash
# Mine with custom thresholds
make skills-mine

# Or use Python directly
python3 services/skillsmith/miner.py --min_hits 3 --top 20
```

## Rejection

If a skill is not useful:

1. Delete the file
2. Comment on the PR explaining why
3. Consider adjusting mining thresholds if too noisy

## Learn More

- [Skillsmith Architecture](../../docs/skillsmith-architecture.md)
- [Error Mining Guide](../../docs/error-mining.md)
- [Makefile Commands](../../Makefile) - Search for `skills-*` targets
