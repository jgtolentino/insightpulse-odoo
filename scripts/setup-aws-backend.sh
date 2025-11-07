#!/bin/bash
# InsightPulse AI - AWS S3 + DynamoDB Backend Setup
# This script creates the necessary AWS resources for OpenTofu/Terraform state management
#
# Prerequisites:
# 1. AWS CLI installed and configured
# 2. AWS credentials with permissions to create S3 buckets and DynamoDB tables
#
# Usage:
#   ./scripts/setup-aws-backend.sh
#
# Cost: ~$0.50/month (vs $20+/month for Terraform Cloud)

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
BUCKET_NAME="${AWS_BUCKET_NAME:-ipai-tofu-state}"
DYNAMODB_TABLE="${AWS_DYNAMODB_TABLE:-ipai-tofu-locks}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed"
        print_info "Install it from: https://aws.amazon.com/cli/"
        exit 1
    fi
    print_success "AWS CLI is installed"
}

# Check AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured"
        print_info "Run: aws configure"
        exit 1
    fi
    print_success "AWS credentials are valid"

    # Display current AWS identity
    AWS_IDENTITY=$(aws sts get-caller-identity --query 'Arn' --output text)
    print_info "Using AWS identity: ${AWS_IDENTITY}"
}

# Create S3 bucket
create_s3_bucket() {
    print_info "Creating S3 bucket: ${BUCKET_NAME}"

    # Check if bucket already exists
    if aws s3 ls "s3://${BUCKET_NAME}" 2>/dev/null; then
        print_warning "Bucket ${BUCKET_NAME} already exists"
        return 0
    fi

    # Create bucket
    if [ "${AWS_REGION}" = "us-east-1" ]; then
        # us-east-1 doesn't require LocationConstraint
        aws s3api create-bucket \
            --bucket "${BUCKET_NAME}" \
            --region "${AWS_REGION}"
    else
        # Other regions require LocationConstraint
        aws s3api create-bucket \
            --bucket "${BUCKET_NAME}" \
            --region "${AWS_REGION}" \
            --create-bucket-configuration LocationConstraint="${AWS_REGION}"
    fi

    print_success "S3 bucket created: ${BUCKET_NAME}"
}

# Enable versioning on S3 bucket
enable_s3_versioning() {
    print_info "Enabling versioning on S3 bucket: ${BUCKET_NAME}"

    aws s3api put-bucket-versioning \
        --bucket "${BUCKET_NAME}" \
        --versioning-configuration Status=Enabled

    print_success "Versioning enabled on ${BUCKET_NAME}"
}

# Enable encryption on S3 bucket
enable_s3_encryption() {
    print_info "Enabling encryption on S3 bucket: ${BUCKET_NAME}"

    aws s3api put-bucket-encryption \
        --bucket "${BUCKET_NAME}" \
        --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }]
        }'

    print_success "Encryption enabled on ${BUCKET_NAME}"
}

# Block public access on S3 bucket
block_public_access() {
    print_info "Blocking public access on S3 bucket: ${BUCKET_NAME}"

    aws s3api put-public-access-block \
        --bucket "${BUCKET_NAME}" \
        --public-access-block-configuration \
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

    print_success "Public access blocked on ${BUCKET_NAME}"
}

# Create DynamoDB table for state locking
create_dynamodb_table() {
    print_info "Creating DynamoDB table: ${DYNAMODB_TABLE}"

    # Check if table already exists
    if aws dynamodb describe-table --table-name "${DYNAMODB_TABLE}" --region "${AWS_REGION}" &> /dev/null; then
        print_warning "DynamoDB table ${DYNAMODB_TABLE} already exists"
        return 0
    fi

    # Create table
    aws dynamodb create-table \
        --table-name "${DYNAMODB_TABLE}" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "${AWS_REGION}"

    print_success "DynamoDB table created: ${DYNAMODB_TABLE}"

    # Wait for table to be active
    print_info "Waiting for DynamoDB table to be active..."
    aws dynamodb wait table-exists --table-name "${DYNAMODB_TABLE}" --region "${AWS_REGION}"
    print_success "DynamoDB table is active"
}

# Display summary
display_summary() {
    echo ""
    echo "======================================"
    echo "AWS Backend Setup Complete!"
    echo "======================================"
    echo ""
    echo "S3 Bucket:        ${BUCKET_NAME}"
    echo "DynamoDB Table:   ${DYNAMODB_TABLE}"
    echo "AWS Region:       ${AWS_REGION}"
    echo ""
    echo "Next steps:"
    echo "1. Update terraform/backend.tf with your bucket name"
    echo "2. Run: cd terraform && tofu init"
    echo "3. Type 'yes' when prompted to migrate state"
    echo ""
    echo "Cost Estimate: ~\$0.50/month"
    echo "  - S3 storage: ~\$0.02/month (for 1GB)"
    echo "  - DynamoDB: ~\$0.00/month (free tier)"
    echo "  - S3 requests: ~\$0.01/month"
    echo ""
}

# Main function
main() {
    echo ""
    echo "======================================"
    echo "InsightPulse AI - AWS Backend Setup"
    echo "======================================"
    echo ""

    print_info "Bucket Name:      ${BUCKET_NAME}"
    print_info "DynamoDB Table:   ${DYNAMODB_TABLE}"
    print_info "AWS Region:       ${AWS_REGION}"
    echo ""

    # Check prerequisites
    check_aws_cli
    check_aws_credentials

    # Create resources
    create_s3_bucket
    enable_s3_versioning
    enable_s3_encryption
    block_public_access
    create_dynamodb_table

    # Display summary
    display_summary
}

# Run main function
main
