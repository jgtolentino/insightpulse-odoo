# Vendored OCA Modules

We vendor core OCA repositories into `addons/oca/*` so ZIP releases and air-gapped installs stay self-contained.

- Run `scripts/fetch_oca.sh` to clone the required repositories (depth=1) into `addons/oca/`.
- After the script completes, remove any nested `.git/` folders (`find addons/oca -name .git -prune -exec rm -rf {} +`).
- Commit the resulting files so the repository, ZIP release, and CI pipelines do not require network access to GitHub.
- Each vendored repository retains its upstream `LICENSE` and documentation for reference.
