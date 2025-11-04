# Docker Hub Publishing - Currently Disabled

This workflow is disabled because:
1. Not using Docker Hub for production deployments
2. Using DigitalOcean App Platform remote builds instead
3. Missing Docker Hub credentials (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)

To re-enable:
1. Set GitHub secrets:
   - DOCKERHUB_USERNAME
   - DOCKERHUB_TOKEN
2. Rename .github/workflows/dockerhub-publish.yml.disabled → dockerhub-publish.yml
3. Update DOCKER_REPO env variable if needed

See docs/CI_CD_AUDIT_2025-11-04.md for details.
