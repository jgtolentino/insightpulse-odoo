# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Apache Superset Production Configuration
# Deployment: DigitalOcean App Platform
# Database: Supabase PostgreSQL
# Date: 2025-10-30

import logging
import os
from typing import Optional

from celery.schedules import crontab
from flask_caching.backends.rediscache import RedisCache

logger = logging.getLogger()

# ========================================
# Environment Configuration
# ========================================

def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """Get environment variable with fallback"""
    value = os.getenv(var_name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {var_name} is not set")
    return value

# ========================================
# Database Configuration (Supabase PostgreSQL)
# ========================================

DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT", "postgresql")
DATABASE_USER = get_env_variable("DATABASE_USER")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = get_env_variable("DATABASE_HOST")
DATABASE_PORT = get_env_variable("DATABASE_PORT", "6543")  # Supabase pooler
DATABASE_DB = get_env_variable("DATABASE_DB", "postgres")

# PostgreSQL connection string with connection pooling
SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
    f"?sslmode=require"  # Enforce SSL for Supabase
    f"&connect_timeout=10"
    f"&application_name=superset"
)

# Connection pool settings for production
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_size": 10,  # Connection pool size
    "max_overflow": 20,  # Max overflow connections
    "pool_recycle": 3600,  # Recycle connections every hour
    "pool_timeout": 30,  # Connection timeout
    "echo": False,  # Disable SQL logging in production
}

# ========================================
# Redis Configuration
# ========================================

REDIS_HOST = get_env_variable("REDIS_HOST", "redis")
REDIS_PORT = get_env_variable("REDIS_PORT", "6379")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Redis URL with optional password
def get_redis_url(db: str) -> str:
    if REDIS_PASSWORD:
        return f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{db}"
    return f"redis://{REDIS_HOST}:{REDIS_PORT}/{db}"

# ========================================
# Cache Configuration
# ========================================

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(get_env_variable("CACHE_DEFAULT_TIMEOUT", "300")),
    "CACHE_KEY_PREFIX": "superset_cache_",
    "CACHE_REDIS_URL": get_redis_url(REDIS_RESULTS_DB),
}

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": int(get_env_variable("DATA_CACHE_DEFAULT_TIMEOUT", "3600")),
    "CACHE_KEY_PREFIX": "superset_data_",
    "CACHE_REDIS_URL": get_redis_url(REDIS_RESULTS_DB),
}

THUMBNAIL_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours
    "CACHE_KEY_PREFIX": "superset_thumbnail_",
    "CACHE_REDIS_URL": get_redis_url(REDIS_RESULTS_DB),
}

RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
    db=int(REDIS_RESULTS_DB),
    key_prefix="superset_results_",
)

# ========================================
# Celery Configuration
# ========================================

class CeleryConfig:
    broker_url = get_redis_url(REDIS_CELERY_DB)
    result_backend = get_redis_url(REDIS_RESULTS_DB)

    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )

    worker_prefetch_multiplier = 1
    task_acks_late = False
    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
        "email_reports.send": {
            "rate_limit": "1/s",
            "time_limit": 600,
            "soft_time_limit": 540,
        },
    }

    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
        "cache-warmup-hourly": {
            "task": "cache-warmup",
            "schedule": crontab(minute=0, hour="*"),  # Every hour
        },
    }

CELERY_CONFIG = CeleryConfig

# ========================================
# Security Configuration
# ========================================

# Secret key for session management (MUST be set in environment)
SECRET_KEY = get_env_variable("SUPERSET_SECRET_KEY")

# Disable debug mode in production
FLASK_DEBUG = False

# Enable Talisman security headers
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    "content_security_policy": {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],  # Required for Superset
        "style-src": ["'self'", "'unsafe-inline'"],  # Required for Superset
        "img-src": ["'self'", "data:", "blob:", "https:"],
        "font-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
        "frame-ancestors": ["'none'"],
    },
    "force_https": True,
    "strict_transport_security": True,
    "strict_transport_security_max_age": 31536000,  # 1 year
    "content_security_policy_nonce_in": ["script-src"],
}

# Session configuration
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # Requires HTTPS
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = 43200  # 12 hours

# WTF CSRF protection
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# CORS configuration (disable by default, enable if needed)
ENABLE_CORS = os.getenv("ENABLE_CORS", "false").lower() == "true"
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": os.getenv("CORS_ORIGINS", "").split(",") if ENABLE_CORS else [],
}

# ========================================
# Application Configuration
# ========================================

# Application root path (for reverse proxy)
APPLICATION_ROOT = os.getenv("SUPERSET_APP_ROOT", "/superset")

# Webserver configuration
SUPERSET_WEBSERVER_PROTOCOL = get_env_variable("SUPERSET_WEBSERVER_PROTOCOL", "https")
SUPERSET_WEBSERVER_ADDRESS = get_env_variable("SUPERSET_WEBSERVER_ADDRESS", "0.0.0.0")
SUPERSET_WEBSERVER_PORT = int(get_env_variable("SUPERSET_WEBSERVER_PORT", "8088"))

# Base URL for emails and notifications
WEBDRIVER_BASEURL = f"{SUPERSET_WEBSERVER_PROTOCOL}://insightpulseai.net{APPLICATION_ROOT}/"
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL

# ========================================
# Feature Flags
# ========================================

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "DASHBOARD_RBAC": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_VIRTUALIZATION": True,
    "EMBEDDED_SUPERSET": False,  # Disable embedding in production
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ENABLE_JAVASCRIPT_CONTROLS": False,  # Disable for security
    "THUMBNAILS": True,
    "THUMBNAILS_SQLA_LISTENERS": True,
}

# ========================================
# Query Configuration
# ========================================

# SQL Lab configuration
SQLLAB_CTAS_NO_LIMIT = True
SQLLAB_TIMEOUT = int(os.getenv("SQLLAB_TIMEOUT", "300"))  # 5 minutes
SQLLAB_ASYNC_TIME_LIMIT_SEC = 3600  # 1 hour for async queries

# Query result limits
SQL_MAX_ROW = 100000
SAMPLES_ROW_LIMIT = 1000
DISPLAY_MAX_ROW = 10000

# ========================================
# Upload Configuration
# ========================================

# CSV upload settings
UPLOAD_FOLDER = "/app/superset_home/uploads"
UPLOAD_CHUNK_SIZE = 4096

# Excel upload settings
EXCEL_EXTENSIONS = {"xlsx", "xls"}
CSV_EXTENSIONS = {"csv", "tsv", "txt"}

# ========================================
# Email Configuration (Optional)
# ========================================

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "true").lower() == "true"
SMTP_SSL = os.getenv("SMTP_SSL", "false").lower() == "true"
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_MAIL_FROM = os.getenv("SMTP_MAIL_FROM", "noreply@insightpulseai.net")

if SMTP_HOST:
    EMAIL_NOTIFICATIONS = True
    EMAIL_HEADER_MUTATOR = lambda x: x  # No-op mutator

# ========================================
# Slack Configuration (Optional)
# ========================================

SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")

# ========================================
# Logging Configuration
# ========================================

# Log level
LOG_LEVEL = os.getenv("SUPERSET_LOG_LEVEL", "WARNING").upper()
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
)

# Disable Flask-Appbuilder info logs
logging.getLogger("flask_appbuilder").setLevel(logging.WARNING)

# ========================================
# Admin Account Configuration
# ========================================

# Admin credentials for initialization
ADMIN_USERNAME = get_env_variable("SUPERSET_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = get_env_variable("SUPERSET_ADMIN_PASSWORD")
ADMIN_FIRST_NAME = get_env_variable("SUPERSET_ADMIN_FIRST_NAME", "Admin")
ADMIN_LAST_NAME = get_env_variable("SUPERSET_ADMIN_LAST_NAME", "User")
ADMIN_EMAIL = get_env_variable("SUPERSET_ADMIN_EMAIL", "admin@insightpulseai.net")

# ========================================
# Rate Limiting
# ========================================

RATELIMIT_ENABLED = True
RATELIMIT_STORAGE_URL = get_redis_url(REDIS_RESULTS_DB)

# ========================================
# Async Query Configuration
# ========================================

GLOBAL_ASYNC_QUERIES = True
GLOBAL_ASYNC_QUERIES_REDIS_CONFIG = {
    "port": int(REDIS_PORT),
    "host": REDIS_HOST,
    "password": REDIS_PASSWORD if REDIS_PASSWORD else None,
    "db": int(REDIS_RESULTS_DB),
}
GLOBAL_ASYNC_QUERIES_REDIS_STREAM_PREFIX = "async-events-"

# ========================================
# Health Check Configuration
# ========================================

HEALTH_CHECK_ENDPOINT = "/health"

# ========================================
# Production Optimizations
# ========================================

# Disable example data in production
SUPERSET_LOAD_EXAMPLES = os.getenv("SUPERSET_LOAD_EXAMPLES", "no").lower() == "yes"

# Enable async query execution
SQLLAB_ASYNC_TIME_LIMIT_SEC = 3600

# Dashboard cache warmup
THUMBNAIL_SELENIUM_USER = "admin"

# Row level security
ROW_LEVEL_SECURITY_ENABLED = True

logger.info("Loaded production Superset configuration")
logger.info(f"Database: {DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}")
logger.info(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
logger.info(f"Application root: {APPLICATION_ROOT}")
logger.info(f"Base URL: {WEBDRIVER_BASEURL}")
