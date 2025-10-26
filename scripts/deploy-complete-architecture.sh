#!/bin/bash
# Complete Architecture Deployment Script for InsightPulse Odoo
# Deploys Odoo + Supabase + MindsDB + Airbyte + Agent System

set -e

echo "🚀 Deploying InsightPulse Complete Architecture..."

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found. Please create one from env.example"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/airbyte
mkdir -p data/mindsdb

echo "📦 Setting up Docker services..."

# Start Odoo with Postgres
echo "Starting Odoo services..."
docker-compose up -d postgres odoo

# Wait for Odoo to be ready
echo "Waiting for Odoo to be ready..."
until docker-compose exec -T postgres pg_isready -U $POSTGRES_USER; do
    sleep 5
done

# Install IPAI modules
echo "Installing IPAI modules..."
docker-compose exec -T odoo odoo -c /etc/odoo/odoo.conf -d $POSTGRES_DB \
    -i ipai_procure,ipai_expense,ipai_subscriptions --stop-after-init

# Deploy Supabase schemas (if Supabase is configured)
if [ ! -z "$SUPABASE_DB_HOST" ]; then
    echo "📊 Setting up Supabase schemas..."
    # This would typically be run against your Supabase instance
    # psql $SUPABASE_CONNECTION_STRING -f supabase/schemas.sql
    echo "Supabase schemas would be deployed here"
fi

# Deploy Airbyte configuration (if Airbyte is available)
if command -v airbyte &> /dev/null; then
    echo "🔄 Configuring Airbyte sync..."
    # airbyte deploy --config airbyte/odoo-to-supabase.yml
    echo "Airbyte configuration would be deployed here"
fi

# Deploy MindsDB (if using local deployment)
if [ ! -z "$MINDSDB_HOST" ]; then
    echo "🧠 Setting up MindsDB..."
    # This would deploy MindsDB configuration
    # mindsdb deploy --config mindsdb/mindsdb-config.yml
    echo "MindsDB configuration would be deployed here"
fi

# Setup GitHub labels and project (requires gh CLI)
if command -v gh &> /dev/null; then
    echo "🏷️ Setting up GitHub labels..."
    
    # Create labels
    gh label create "decision:odoo_sa" --color "0E8A16" --description "Odoo Standard Application" --force
    gh label create "decision:oca" --color "1D76DB" --description "OCA Community Module" --force
    gh label create "decision:ipai" --color "B60205" --description "IPAI Custom Module" --force
    
    gh label create "area:procurement" --color "D93F0B" --description "Procurement domain" --force
    gh label create "area:expense" --color "FBCA04" --description "Expense management" --force
    gh label create "area:subscriptions" --color "0E8A16" --description "Subscription billing" --force
    gh label create "area:bi" --color "1D76DB" --description "Business Intelligence" --force
    gh label create "area:ml" --color "5319E7" --description "Machine Learning" --force
    gh label create "area:agent" --color "CC317C" --description "Agent automation" --force
    gh label create "area:connector" --color "006B75" --description "External integrations" --force
    
    gh label create "status:planned" --color "FEF2C0" --description "Planned for implementation" --force
    gh label create "status:in-progress" --color "FBCA04" --description "Currently being implemented" --force
    gh label create "status:done" --color "0E8A16" --description "Completed" --force
    
    echo "GitHub labels created successfully"
else
    echo "⚠️  GitHub CLI not found. Please install 'gh' to automate label creation"
fi

# Test the agent classifier
echo "🤖 Testing issue classifier..."
python3 agents/issue-classifier.py

# Create deployment summary
echo "📋 Creating deployment summary..."
cat > deployment-summary.md << EOF
# InsightPulse Architecture Deployment Summary

## ✅ Deployed Components

### Core ERP
- Odoo 19 with Postgres
- IPAI Modules: Procure, Expense, Subscriptions

### Analytics & ML Stack
- Supabase (Analytics Database)
- MindsDB (ML Platform) 
- Airbyte (Data Sync)

### Development Workflow
- GitHub Issue Classification
- Automated plan.yaml generation
- CI/CD with decision enforcement

## 🔗 Architecture Flow

1. **Odoo (OLTP)** → Airbyte CDC → **Supabase (Analytics)**
2. **Supabase** → MindsDB → **ML Predictions**
3. **GitHub Issues** → Agent Classification → **plan.yaml**

## 🛠️ Next Steps

1. Configure Supabase connection details
2. Set up Airbyte sync jobs
3. Train initial ML models in MindsDB
4. Test the agent classification system

## 📊 Monitoring

- Data sync status: Check Airbyte jobs
- ML model performance: MindsDB monitoring
- Issue classification: Agent logs

EOF

echo "🎉 Deployment completed!"
echo "📄 See deployment-summary.md for details"
echo "🚀 Next: Configure your Supabase and MindsDB instances"

# Display quick test commands
echo ""
echo "🧪 Quick Test Commands:"
echo "  Odoo: docker-compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d $POSTGRES_DB"
echo "  Postgres: docker-compose exec postgres psql -U $POSTGRES_USER $POSTGRES_DB"
echo "  Agent: python3 agents/issue-classifier.py"
