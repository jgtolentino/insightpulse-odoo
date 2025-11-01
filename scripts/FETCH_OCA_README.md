# OCA Fetch Script Documentation

## fetch_oca.sh

**Purpose**: Lightweight Docker build-time script for fetching OCA (Odoo Community Association) modules into the container image.

### Overview

This script is designed to run **inside the Dockerfile** during the build process to fetch OCA repositories. It differs from `sync-oca-repos.sh` which is intended for local development environments.

### Key Features

- **Build-time optimization**: Uses shallow clones (`--depth 1`) to minimize image size
- **Simple format**: Reads a plain text file with "REPO_URL BRANCH" format
- **Comment support**: Skips lines starting with `#` and empty lines
- **Error handling**: Validates file existence, malformed lines, and git clone failures
- **Robust variable handling**: Properly quoted variables for path safety
- **Docker-focused**: Designed for CI/CD and container builds
- **Minimal dependencies**: Only requires git and bash

### Usage

```bash
./scripts/fetch_oca.sh <repo_list_file> <destination_dir>
```

**Parameters:**
- `repo_list_file`: Path to text file containing repository URLs and branches
- `destination_dir`: Target directory for cloned repositories

**Example:**
```bash
./scripts/fetch_oca.sh vendor/oca_requirements.txt /mnt/extra-addons/oca
```

### Repository List Format

The `vendor/oca_requirements.txt` file should contain one repository per line:

```
# OCA Requirements for Docker Build
# Format: REPO_URL BRANCH

https://github.com/OCA/contract 19.0
https://github.com/OCA/server-tools 19.0
https://github.com/OCA/reporting-engine 19.0
```

**Format**: `REPO_URL BRANCH`

**Features**:
- Lines starting with `#` are treated as comments and skipped
- Empty lines are ignored
- Whitespace-only lines are skipped
- Supports both `.git` and non-`.git` URLs (automatically handled)

### Integration with Dockerfile

Add to your Dockerfile:

```dockerfile
# Copy OCA requirements and fetch script
COPY vendor/oca_requirements.txt /tmp/oca_requirements.txt
COPY scripts/fetch_oca.sh /tmp/fetch_oca.sh
RUN chmod +x /tmp/fetch_oca.sh

# Fetch OCA modules during build
RUN /tmp/fetch_oca.sh /tmp/oca_requirements.txt /mnt/extra-addons/oca
```

### Comparison with sync-oca-repos.sh

| Feature | fetch_oca.sh | sync-oca-repos.sh |
|---------|--------------|-------------------|
| **Use case** | Docker build | Local development |
| **Clone depth** | Shallow (depth 1) | Full history |
| **Config format** | Simple text file | Hardcoded array |
| **Repos** | Configured (3-5) | Comprehensive (30+) |
| **Output** | Minimal logging | Rich UI with colors |
| **Update support** | No (build fresh) | Yes (fetch/update) |

### Configuration Files

- **`vendor/oca_requirements.txt`**: Simple list for Docker builds (used by this script)
- **`vendor/oca_repos.yml`**: Structured YAML with module-level detail
- **`vendor/oca_repos.lock`**: Version pinning and compatibility matrix

### See Also

- **`sync-oca-repos.sh`**: Comprehensive OCA sync for local development
- **`vendor_oca.py`**: OCA module vendoring and indexing
- **`copy-addons.sh`**: Conditional addon copying for Docker builds

### Maintenance

When adding new OCA repositories to production builds:

1. Update `vendor/oca_requirements.txt` with the new repo and branch
2. Optionally update `vendor/oca_repos.yml` for documentation
3. Rebuild the Docker image
4. Update `vendor/oca_repos.lock` if pinning versions

### Related Documentation

- OCA module structure: `docs/claude-code-skills/odoo/reference/oca-module-structure.md`
- OCA vendoring patterns: `docs/claude-code-skills/odoo/reference/oca-vendoring.md`
- Main README: `README.md` (OCA integration section)
