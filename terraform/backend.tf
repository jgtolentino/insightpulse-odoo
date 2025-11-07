# InsightPulse AI - OpenTofu/Terraform Backend Configuration
# AWS S3 + DynamoDB for state management and locking
#
# This replaces Terraform Cloud and provides:
# - State storage in S3 (versioned, encrypted)
# - State locking via DynamoDB (prevents concurrent modifications)
# - Cost: ~$0.50/month (vs $20+/month for Terraform Cloud)
#
# Setup Instructions:
# 1. Run: ./scripts/setup-aws-backend.sh
# 2. Run: tofu init (or terraform init)
# 3. Type 'yes' when prompted to migrate state

terraform {
  backend "s3" {
    # S3 bucket for state storage (must be globally unique)
    # Replace this with your own bucket name
    bucket = "ipai-tofu-state"

    # State file path within the bucket
    # This allows multiple environments to share the same bucket
    key = "insightpulse/odoo-stack/terraform.tfstate"

    # AWS region for S3 and DynamoDB
    region = "us-east-1"

    # DynamoDB table for state locking
    # Prevents multiple users from modifying state simultaneously
    dynamodb_table = "ipai-tofu-locks"

    # Encryption for state file at rest
    encrypt = true

    # Additional S3 settings
    # These enable better reliability and consistency
    acl = "private"

    # Workspace prefix for multi-environment support
    # workspace_key_prefix = "env"  # Uncomment for workspace support
  }
}

# NOTE: If you're migrating from DigitalOcean Spaces or another backend:
# 1. Comment out the old backend configuration in main.tf
# 2. Run: tofu init -migrate-state
# 3. Follow the prompts to migrate your existing state
#
# To use DigitalOcean Spaces instead of AWS S3:
# 1. Replace the backend "s3" block above with:
#    backend "s3" {
#      endpoint                    = "sgp1.digitaloceanspaces.com"
#      region                      = "us-east-1"  # Required but not used
#      bucket                      = "insightpulse-terraform-state"
#      key                         = "production/terraform.tfstate"
#      skip_credentials_validation = true
#      skip_metadata_api_check     = true
#      skip_region_validation      = true
#    }
# 2. Note: DigitalOcean Spaces does NOT support DynamoDB locking
