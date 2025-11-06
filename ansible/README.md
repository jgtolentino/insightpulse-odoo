# Ansible Playbooks - InsightPulse AI

Configuration management and automation playbooks for InsightPulse AI infrastructure.

## 📋 Prerequisites

```bash
# Install Ansible
pip install ansible

# Verify installation
ansible --version
```

## 📁 Directory Structure

```
ansible/
├── playbooks/
│   ├── server-setup.yml          # Initial server setup
│   └── deploy-monitoring.yml     # Deploy monitoring stack
├── inventory/
│   └── production.ini            # Production inventory
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Configure Inventory

Edit `inventory/production.ini` with your server IPs:

```ini
[monitoring]
monitoring-server ansible_host=192.0.2.10 ansible_user=admin
```

### 2. Test Connectivity

```bash
ansible all -i inventory/production.ini -m ping
```

### 3. Run Playbooks

**Setup new server**:
```bash
ansible-playbook -i inventory/production.ini playbooks/server-setup.yml
```

**Deploy monitoring stack**:
```bash
ansible-playbook -i inventory/production.ini playbooks/deploy-monitoring.yml
```

## 📖 Playbook Documentation

### server-setup.yml

Sets up a new Ubuntu server with:
- Security hardening (SSH, UFW, Fail2Ban)
- Automatic security updates
- Docker and Docker Compose
- Monitoring agent (node_exporter)

**Usage**:
```bash
ansible-playbook -i inventory/production.ini \
  playbooks/server-setup.yml \
  --ask-become-pass
```

### deploy-monitoring.yml

Deploys the complete monitoring stack:
- Prometheus
- Grafana
- Alertmanager
- Node Exporter
- cAdvisor
- Blackbox Exporter

**Usage**:
```bash
# Set environment variables
export GRAFANA_ADMIN_PASSWORD=your-password
export SUPABASE_DB_HOST=your-db-host
export SUPABASE_DB_PASSWORD=your-db-password

# Run playbook
ansible-playbook -i inventory/production.ini \
  playbooks/deploy-monitoring.yml
```

## 🔐 Security Best Practices

1. **Use Ansible Vault for Secrets**:
   ```bash
   ansible-vault create secrets.yml
   ansible-playbook playbook.yml --ask-vault-pass
   ```

2. **SSH Key Authentication**:
   - Never use password authentication
   - Use separate SSH keys for different environments

3. **Least Privilege**:
   - Use `become: yes` only when necessary
   - Create service-specific users

## 📄 License

Part of InsightPulse AI platform.
