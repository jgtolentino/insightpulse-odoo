# InsightPulse AI - OpenTofu/Terraform Backend Configuration
# DigitalOcean Spaces for state management (S3-compatible)
#
# This replaces Terraform Cloud and provides:
# - State storage in DigitalOcean Spaces (S3-compatible, versioned)
# - Cost: $5/month (includes 250GB storage + 1TB transfer)
# - No additional cloud provider dependencies
#
# Setup Instructions:
# 1. Run: ./scripts/setup-digitalocean-backend.sh
# 2. Set credentials: export AWS_ACCESS_KEY_ID="your-spaces-key"
#                     export AWS_SECRET_ACCESS_KEY="your-spaces-secret"
# 3. Run: tofu init (or terraform init)
# 4. Type 'yes' when prompted to migrate state
#
# Note: DigitalOcean Spaces does NOT support state locking.
# Only one person should run "tofu apply" at a time.

terraform {
  backend "s3" {
    # DigitalOcean Spaces endpoint (Singapore region)
    # Change to your preferred region: nyc3, sfo3, ams3, sgp1, fra1
    endpoint = "sgp1.digitaloceanspaces.com"

    # Region is required but not used by DigitalOcean Spaces
    region = "us-east-1"

    # Space name (must be globally unique)
    bucket = "insightpulse-terraform-state"

    # State file path within the Space
    key = "production/terraform.tfstate"

    # Skip AWS-specific validations (required for DigitalOcean Spaces)
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true

    # Force path-style URLs (required for DigitalOcean Spaces)
    force_path_style = false
  }
}

# IMPORTANT: State Locking
# DigitalOcean Spaces does NOT support DynamoDB-style state locking.
#
# Best practices for team collaboration:
# 1. Use a shared Slack/Teams channel to coordinate deployments
# 2. Create a deployment schedule (e.g., "John deploys Mon/Wed, Jane Tue/Thu")
# 3. Always run "tofu plan" first to check for conflicts
# 4. Consider using Terraform Cloud for state locking if needed (~$20/month)
#
# Alternative: Use GitOps workflow
# - All changes go through pull requests
# - CI/CD pipeline runs "tofu apply"
# - Only automated system has write access to state
