# DigitalOcean App Platform Applications

# Odoo SaaS Platform App
resource "digitalocean_app" "odoo_saas" {
  spec {
    name   = "odoo-saas-platform"
    region = var.region

    service {
      name               = "odoo-web"
      instance_count     = var.app_instance_count
      instance_size_slug = var.app_instance_size

      github {
        repo           = "jgtolentino/insightpulse-odoo"
        branch         = "main"
        deploy_on_push = true
      }

      dockerfile_path = "Dockerfile"
      http_port       = 8069

      health_check {
        http_path             = "/web/health"
        initial_delay_seconds = 180
        period_seconds        = 30
        timeout_seconds       = 10
        success_threshold     = 1
        failure_threshold     = 3
      }

      # Database configuration
      env {
        key   = "ODOO_DB_HOST"
        value = var.supabase_db_host
      }

      env {
        key   = "ODOO_DB_PORT"
        value = tostring(var.supabase_db_port)
      }

      env {
        key   = "ODOO_DB_NAME"
        value = var.supabase_db_name
      }

      env {
        key   = "ODOO_DB_USER"
        value = var.supabase_db_user
      }

      env {
        key   = "ODOO_DB_PASSWORD"
        value = var.supabase_db_password
        type  = "SECRET"
      }

      # Odoo configuration
      env {
        key   = "ODOO_ADMIN_PASSWORD"
        value = var.odoo_admin_password
        type  = "SECRET"
      }

      env {
        key   = "ODOO_WORKERS"
        value = tostring(var.odoo_workers)
      }

      env {
        key   = "ODOO_MAX_CRON_THREADS"
        value = "1"
      }

      env {
        key   = "ODOO_DB_MAXCONN"
        value = tostring(var.odoo_db_maxconn)
      }

      env {
        key   = "ODOO_LIMIT_MEMORY_HARD"
        value = "419430400"  # 400MB
      }

      env {
        key   = "ODOO_LIMIT_MEMORY_SOFT"
        value = "335544320"  # 320MB
      }

      env {
        key   = "ODOO_LIMIT_TIME_CPU"
        value = "300"
      }

      env {
        key   = "ODOO_LIMIT_TIME_REAL"
        value = "600"
      }

      env {
        key   = "ODOO_ADDONS_PATH"
        value = "/mnt/extra-addons/insightpulse,/mnt/extra-addons/custom,/mnt/extra-addons/oca,/usr/lib/python3/dist-packages/odoo/addons"
      }

      # AI configuration
      env {
        key   = "AI_PROVIDER"
        value = "ollama"
      }

      env {
        key   = "OLLAMA_BASE_URL"
        value = "https://llm.insightpulseai.net"
      }

      env {
        key   = "OLLAMA_MODEL"
        value = "llama3.2:3b"
      }

      routes {
        path = "/"
      }
    }

    domain {
      name = "erp.insightpulseai.net"
    }
  }
}

# Superset Analytics App
resource "digitalocean_app" "superset" {
  spec {
    name   = "superset-analytics"
    region = var.region

    service {
      name               = "superset"
      instance_count     = var.app_instance_count
      instance_size_slug = var.app_instance_size

      github {
        repo           = "jgtolentino/insightpulse-odoo"
        branch         = "main"
        deploy_on_push = true
      }

      dockerfile_path = "docker/superset/Dockerfile"
      http_port       = 8088

      health_check {
        http_path             = "/health"
        initial_delay_seconds = 60
        period_seconds        = 30
        timeout_seconds       = 5
        success_threshold     = 1
        failure_threshold     = 3
      }

      env {
        key   = "SUPERSET_SECRET_KEY"
        value = "insightpulse-superset-secret-2025"
        type  = "SECRET"
      }

      env {
        key   = "POSTGRES_DB"
        value = var.supabase_db_name
      }

      env {
        key   = "POSTGRES_USER"
        value = var.supabase_db_user
      }

      env {
        key   = "POSTGRES_PASSWORD"
        value = var.supabase_db_password
        type  = "SECRET"
      }

      env {
        key   = "POSTGRES_HOST"
        value = var.supabase_db_host
      }

      env {
        key   = "POSTGRES_PORT"
        value = tostring(var.supabase_db_port)
      }

      routes {
        path = "/"
      }
    }

    domain {
      name = "superset.insightpulseai.net"
    }
  }
}

# MCP Server App
resource "digitalocean_app" "mcp_server" {
  spec {
    name   = "pulser-hub-mcp"
    region = var.region

    service {
      name               = "mcp-server"
      instance_count     = var.app_instance_count
      instance_size_slug = var.app_instance_size

      github {
        repo           = "jgtolentino/insightpulse-odoo"
        branch         = "main"
        deploy_on_push = true
      }

      source_dir      = "services/mcp-server"
      dockerfile_path = "services/mcp-server/Dockerfile"
      http_port       = 8000

      health_check {
        http_path             = "/health"
        initial_delay_seconds = 10
        period_seconds        = 30
        timeout_seconds       = 3
        success_threshold     = 1
        failure_threshold     = 3
      }

      env {
        key   = "GITHUB_APP_ID"
        value = var.github_app_id
      }

      env {
        key   = "GITHUB_PRIVATE_KEY"
        value = var.github_private_key
        type  = "SECRET"
      }

      env {
        key   = "GITHUB_INSTALLATION_ID"
        value = var.github_installation_id
        type  = "SECRET"
      }

      routes {
        path = "/mcp/github"
      }

      routes {
        path = "/health"
      }

      routes {
        path = "/"
      }
    }

    domain {
      name = "mcp.insightpulseai.net"
    }
  }
}

# InsightPulse Monitor App
resource "digitalocean_app" "monitor" {
  spec {
    name   = "insightpulse-monitor"
    region = var.region

    service {
      name               = "monitor"
      instance_count     = var.app_instance_count
      instance_size_slug = var.app_instance_size

      github {
        repo           = "jgtolentino/insightpulse-odoo"
        branch         = "main"
        deploy_on_push = true
      }

      source_dir      = "services/insightpulse-monitor"
      dockerfile_path = "services/insightpulse-monitor/Dockerfile"
      http_port       = 5000

      health_check {
        http_path             = "/health"
        initial_delay_seconds = 30
        period_seconds        = 30
        timeout_seconds       = 5
        success_threshold     = 1
        failure_threshold     = 3
      }

      env {
        key   = "SUPABASE_URL"
        value = "https://spdtwktxdalcfigzeqrz.supabase.co"
      }

      env {
        key   = "SUPABASE_KEY"
        value = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        type  = "SECRET"
      }

      env {
        key   = "ODOO_URL"
        value = "https://erp.insightpulseai.net"
      }

      routes {
        path = "/"
      }
    }
  }
}
