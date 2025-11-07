# DigitalOcean Droplets for InsightPulse AI

# PaddleOCR + Ollama LLM Droplet
resource "digitalocean_droplet" "paddleocr" {
  name   = "insightpulse-ocr-llm"
  region = var.region
  size   = var.droplet_size_small
  image  = var.droplet_image

  vpc_uuid = digitalocean_vpc.insightpulse_vpc.id

  ssh_keys = [
    digitalocean_ssh_key.insightpulse_admin.id
  ]

  tags = [
    digitalocean_tag.production.id,
    digitalocean_tag.insightpulse.id,
    "ocr",
    "llm"
  ]

  monitoring = var.enable_monitoring
  backups    = var.enable_backups

  user_data = file("${path.module}/cloud-init/ocr-llm-setup.sh")

  lifecycle {
    create_before_destroy = true
  }
}

# Prometheus + Grafana Monitoring Droplet
resource "digitalocean_droplet" "monitoring" {
  name   = "insightpulse-monitoring"
  region = var.region
  size   = var.droplet_size_medium  # 2GB RAM for Prometheus
  image  = var.droplet_image

  vpc_uuid = digitalocean_vpc.insightpulse_vpc.id

  ssh_keys = [
    digitalocean_ssh_key.insightpulse_admin.id
  ]

  tags = [
    digitalocean_tag.production.id,
    digitalocean_tag.insightpulse.id,
    digitalocean_tag.monitoring.id
  ]

  monitoring = var.enable_monitoring
  backups    = var.enable_backups

  user_data = file("${path.module}/cloud-init/monitoring-setup.sh")

  lifecycle {
    create_before_destroy = true
  }
}

# Volume for Prometheus data persistence
resource "digitalocean_volume" "prometheus_data" {
  region                  = var.region
  name                    = "prometheus-data"
  size                    = 10  # 10GB
  initial_filesystem_type = "ext4"
  description             = "Prometheus time-series data storage"

  lifecycle {
    prevent_destroy = true
  }
}

# Attach volume to monitoring droplet
resource "digitalocean_volume_attachment" "prometheus_data_attachment" {
  droplet_id = digitalocean_droplet.monitoring.id
  volume_id  = digitalocean_volume.prometheus_data.id
}

# Volume for Grafana data persistence
resource "digitalocean_volume" "grafana_data" {
  region                  = var.region
  name                    = "grafana-data"
  size                    = 5  # 5GB
  initial_filesystem_type = "ext4"
  description             = "Grafana dashboards and configuration storage"

  lifecycle {
    prevent_destroy = true
  }
}

# Attach volume to monitoring droplet
resource "digitalocean_volume_attachment" "grafana_data_attachment" {
  droplet_id = digitalocean_droplet.monitoring.id
  volume_id  = digitalocean_volume.grafana_data.id
}

# Firewall for OCR/LLM Droplet
resource "digitalocean_firewall" "ocr_llm_firewall" {
  name = "insightpulse-ocr-llm-firewall"

  droplet_ids = [digitalocean_droplet.paddleocr.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.admin_ip_whitelist
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "8000"  # PaddleOCR API
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "11434"  # Ollama API
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Firewall for Monitoring Droplet
resource "digitalocean_firewall" "monitoring_firewall" {
  name = "insightpulse-monitoring-firewall"

  droplet_ids = [digitalocean_droplet.monitoring.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.admin_ip_whitelist
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "9090"  # Prometheus
    source_addresses = var.admin_ip_whitelist
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "3000"  # Grafana
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Allow metrics collection from VPC
  inbound_rule {
    protocol    = "tcp"
    port_range  = "9090"
    source_tags = ["insightpulse"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Outputs are now consolidated in outputs.tf
