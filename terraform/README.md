# InsightPulse AI - Infrastructure as Code

> **OpenTofu/Terraform configuration for deploying the complete InsightPulse AI stack on DigitalOcean**

Complete Infrastructure as Code (IaC) for InsightPulse AI platform on DigitalOcean with AWS S3 + DynamoDB backend.

## 📁 Directory Structure

```
terraform/
├── backend.tf                 # AWS S3 + DynamoDB backend configuration
├── main.tf                    # Core infrastructure (VPC, firewall, monitoring)
├── variables.tf               # Variable definitions
├── apps.tf                    # DigitalOcean App Platform applications
├── droplets.tf                # Droplet and volume configurations
├── dns.tf                     # DNS records for all services
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example variables file
├── README.md                  # This file
└── cloud-init/
    ├── ocr-llm-setup.sh      # PaddleOCR + Ollama setup script
    └── monitoring-setup.sh    # Prometheus + Grafana setup script
```

## 🏗️ Infrastructure Components

### App Platform Services ($5/month each)
- **Odoo ERP** (erp.insightpulseai.net) - Enterprise resource planning
- **Superset Analytics** (superset.insightpulseai.net) - Business intelligence
- **MCP Server** (mcp.insightpulseai.net) - Model Context Protocol server
- **Monitor Service** - System health monitoring

### Droplets
- **OCR/LLM Droplet** (s-1vcpu-1gb, $6/month) - PaddleOCR + Ollama Llama 3.2 3B
- **Monitoring Droplet** (s-2vcpu-2gb, $18/month) - Prometheus + Grafana stack

### Network Infrastructure
- **VPC** (10.10.0.0/16) - Private networking
- **Firewalls** - Security rules for web, database, and monitoring
- **DNS Records** - Complete domain management for insightpulseai.net

### Storage
- **Prometheus Volume** (10GB) - Time-series metrics data
- **Grafana Volume** (5GB) - Dashboard configurations

## 🚀 Quick Start

### Prerequisites

1. **OpenTofu or Terraform installed**
   ```bash
   # Install OpenTofu (recommended)
   brew install opentofu

   # OR install Terraform
   brew install terraform
   ```

2. **AWS CLI installed and configured** (for state management)
   ```bash
   brew install awscli
   aws configure
   ```

3. **DigitalOcean Account**
   - Create an account at https://digitalocean.com
   - Generate a Personal Access Token (Settings → API → Generate New Token)

### Initial Setup

1. **Set up AWS backend** (for state management)
   ```bash
   # Run the setup script
   ./scripts/setup-aws-backend.sh

   # This creates:
   # - S3 bucket: ipai-tofu-state (with versioning and encryption)
   # - DynamoDB table: ipai-tofu-locks (for state locking)
   # Cost: ~$0.50/month vs $20+/month for Terraform Cloud
   ```

2. **Configure variables**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   vim terraform.tfvars  # Fill in your values
   ```

3. **Initialize OpenTofu/Terraform**
   ```bash
   tofu init  # or: terraform init
   ```

4. **Review the plan**
   ```bash
   tofu plan  # or: terraform plan
   ```

5. **Apply the infrastructure**
   ```bash
   tofu apply  # or: terraform apply
   ```

## 🔧 Configuration

### Required Variables

Edit `terraform.tfvars` with your specific values:

```hcl
# Cloud Provider Credentials
do_token               = "dop_v1_xxxxx"
aws_access_key         = "AKIAIOSFODNN7EXAMPLE"
aws_secret_key         = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# SSH Configuration
ssh_public_key         = "ssh-rsa AAAAB3..."

# Database Configuration
supabase_db_password   = "your-db-password"

# Odoo Configuration
odoo_admin_password    = "your-odoo-password"

# GitHub Configuration
github_private_key     = "-----BEGIN RSA PRIVATE KEY-----\n..."
github_installation_id = "12345678"
```

### Optional Customizations

- **Region**: Change `region` to deploy to different location (default: sgp1)
- **Instance Sizes**: Adjust `droplet_size_*` and `app_instance_size` for different performance
- **Monitoring**: Set `enable_monitoring = false` to disable (not recommended)
- **Backups**: Set `enable_backups = false` to save costs (not recommended)

## 📊 Monitoring & Observability

### Prometheus Metrics

Access Prometheus at: `https://prometheus.insightpulseai.net`

**Metrics collected:**
- System metrics (CPU, memory, disk, network)
- Application metrics (Odoo, Superset, MCP)
- HTTP endpoint health checks
- Custom business metrics

### Grafana Dashboards

Access Grafana at: `https://monitoring.insightpulseai.net`

**Default credentials:**
- Username: `admin`
- Password: `insightpulse2025` (change after first login)

**Pre-configured dashboards:**
- System Overview (CPU, memory, disk across all services)
- Application Performance (response times, request rates)
- Business Metrics (Odoo users, Superset queries)
- Alert Status (active alerts, alert history)

### Alerting Rules

Configured alerts (sent via email):
- Service downtime (>2 minutes)
- High CPU usage (>80% for 5 minutes)
- High memory usage (>85% for 5 minutes)
- Low disk space (<15%)
- HTTP endpoint failures
- Database connection issues

## 🔐 Security

### Firewall Rules

**Web Services** (ports 80, 443):
- Open to public (0.0.0.0/0)

**SSH** (port 22):
- Restricted to `admin_ip_whitelist` IPs only
- Configure this in terraform.tfvars

**Monitoring** (ports 3000, 9090):
- Grafana: Open to public (protected by authentication)
- Prometheus: Restricted to admin IPs (basic auth required)

**Internal Services**:
- VPC-only communication for database traffic
- Service-to-service metrics collection via private network

### Secrets Management

**Stored in Terraform state:**
- Database passwords
- API tokens
- GitHub private keys

**Best practices:**
1. Store `terraform.tfstate` in encrypted S3/Spaces bucket
2. Enable state locking
3. Use Terraform Cloud for team collaboration
4. Never commit `terraform.tfvars` to git (added to .gitignore)

## 💰 Cost Estimation

| Resource | Monthly Cost |
|----------|--------------|
| Odoo App (basic-xxs) | $5 |
| Superset App (basic-xxs) | $5 |
| MCP Server App (basic-xxs) | $5 |
| Monitor App (basic-xxs) | $5 |
| OCR/LLM Droplet (s-1vcpu-1gb) | $6 |
| Monitoring Droplet (s-2vcpu-2gb) | $18 |
| Volumes (15GB total) | $1.50 |
| **Total** | **~$45.50/month** |

*Costs exclude:*
- Supabase (free tier for <500MB)
- Bandwidth overages
- Additional backups
- Reserved IPs ($4/month each)

## 📦 State Management

### Backend: AWS S3 + DynamoDB

**Why AWS S3 instead of Terraform Cloud?**
- ✅ **Cost:** ~$0.50/month vs $20+/month
- ✅ **Control:** Full control over state files
- ✅ **Privacy:** State files stay in your AWS account
- ✅ **Reliability:** S3 offers 99.999999999% durability
- ✅ **No vendor lock-in:** Open-source compatible

**Features:**
- ✅ **Versioning:** S3 bucket versioning enabled
- ✅ **Encryption:** AES-256 encryption at rest
- ✅ **Locking:** DynamoDB prevents concurrent modifications
- ✅ **Backup:** State file versions retained

**Configuration:**
```hcl
terraform {
  backend "s3" {
    bucket         = "ipai-tofu-state"
    key            = "insightpulse/odoo-stack/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "ipai-tofu-locks"
    encrypt        = true
  }
}
```

**Setup:**
```bash
# Run the automated setup script
./scripts/setup-aws-backend.sh

# Or manually create resources:
aws s3api create-bucket --bucket ipai-tofu-state --region us-east-1
aws s3api put-bucket-versioning --bucket ipai-tofu-state --versioning-configuration Status=Enabled
aws dynamodb create-table --table-name ipai-tofu-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region us-east-1
```

### Migrating from DigitalOcean Spaces

If you're migrating from the old DigitalOcean Spaces backend:

```bash
# 1. Set up AWS backend
./scripts/setup-aws-backend.sh

# 2. Update backend.tf with your bucket name
vim terraform/backend.tf

# 3. Initialize and migrate
cd terraform
tofu init -migrate-state

# 4. Type 'yes' when prompted
```

## 🔄 Common Operations

### Update Infrastructure

```bash
# Review changes
terraform plan

# Apply updates
terraform apply
```

### Scale Applications

Edit `terraform.tfvars`:
```hcl
app_instance_count = 2  # Scale to 2 instances
```

Apply changes:
```bash
terraform apply
```

### Add New Droplet

Edit `droplets.tf` and add:
```hcl
resource "digitalocean_droplet" "new_service" {
  name   = "new-service"
  region = var.region
  size   = var.droplet_size_small
  image  = var.droplet_image
  vpc_uuid = digitalocean_vpc.insightpulse_vpc.id
  ssh_keys = [digitalocean_ssh_key.insightpulse_admin.id]
}
```

### Destroy Infrastructure

**⚠️ WARNING: This will delete ALL resources!**

```bash
terraform destroy
```

For specific resource:
```bash
terraform destroy -target=digitalocean_droplet.monitoring
```

## 🧪 Testing

### Validate Configuration

```bash
terraform validate
```

### Check Formatting

```bash
terraform fmt -check
```

### Plan Without Applying

```bash
terraform plan -out=tfplan
```

## 📝 Outputs

After successful `terraform apply`, you'll get:

```
Outputs:

odoo_url = "https://erp.insightpulseai.net"
superset_url = "https://superset.insightpulseai.net"
mcp_server_url = "https://mcp.insightpulseai.net"
ocr_droplet_ip = "192.0.2.10"
monitoring_droplet_ip = "192.0.2.20"
prometheus_url = "http://192.0.2.20:9090"
grafana_url = "http://192.0.2.20:3000"
vpc_id = "vpc-12345678-1234-1234-1234-123456789012"
```

## 🐛 Troubleshooting

### Error: "Error creating droplet"
- Check your DigitalOcean API token
- Verify your account has sufficient resources
- Check region availability: `doctl compute region list`

### Error: "Error creating app"
- Verify GitHub repository access
- Check branch name is correct
- Ensure Dockerfile paths exist

### State Lock Issues
```bash
# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

### DNS Not Resolving
- Wait 5-10 minutes for DNS propagation
- Verify domain ownership in DigitalOcean console
- Check nameservers point to DigitalOcean

## 🔗 References

- [Terraform DigitalOcean Provider](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
- [DigitalOcean API Documentation](https://docs.digitalocean.com/reference/api/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

## 📄 License

Part of InsightPulse AI platform. See main repository LICENSE.
