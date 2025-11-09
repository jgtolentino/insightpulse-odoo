# Apache Superset Configuration for InsightPulse AI
# Production configuration with Odoo integration

import os
from datetime import timedelta
from typing import Optional

# Security
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', 'CHANGE_ME_IN_PRODUCTION')
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Database (Superset metadata store)
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{os.getenv('DATABASE_USER', 'postgres')}:"
    f"{os.getenv('DATABASE_PASSWORD', 'postgres')}@"
    f"{os.getenv('DATABASE_HOST', 'postgres')}:"
    f"{os.getenv('DATABASE_PORT', '5432')}/"
    f"{os.getenv('DATABASE_DB', 'superset')}"
)

# Prevent database modifications through UI
PREVENT_UNSAFE_DB_CONNECTIONS = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_POOL_TIMEOUT = 300
SQLALCHEMY_MAX_OVERFLOW = 20
SQLALCHEMY_POOL_RECYCLE = 3600

# Redis cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': os.getenv('REDIS_HOST', 'redis'),
    'CACHE_REDIS_PORT': int(os.getenv('REDIS_PORT', 6379)),
    'CACHE_REDIS_DB': int(os.getenv('REDIS_DB', 1)),
}

# Celery configuration for async queries and reports
class CeleryConfig:
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
    imports = ('superset.sql_lab', 'superset.tasks.scheduler')

    # Task configuration
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
        'email_reports.send': {
            'rate_limit': '1/s',
            'time_limit': 120,
            'soft_time_limit': 150,
            'ignore_result': True,
        },
    }

    # Celery beat schedule for periodic tasks
    beat_schedule = {
        'reports.scheduler': {
            'task': 'reports.scheduler',
            'schedule': timedelta(minutes=1),
        },
        'reports.prune_log': {
            'task': 'reports.prune_log',
            'schedule': timedelta(hours=1),
        },
    }

CELERY_CONFIG = CeleryConfig

# Feature flags
FEATURE_FLAGS = {
    # Enable alerts and reports
    'ALERT_REPORTS': True,

    # Dashboard features
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_NATIVE_FILTERS_SET': True,
    'DASHBOARD_FILTERS_EXPERIMENTAL': True,

    # SQL Lab features
    'ENABLE_TEMPLATE_PROCESSING': True,
    'ENABLE_TEMPLATE_REMOVE_FILTERS': True,
    'SQLLAB_BACKEND_PERSISTENCE': True,
    'SQL_VALIDATORS_BY_ENGINE': False,

    # Data exploration
    'ENABLE_EXPLORE_DRAG_AND_DROP': True,
    'ENABLE_EXPLORE_JSON_CSRF_PROTECTION': True,

    # Global async queries
    'GLOBAL_ASYNC_QUERIES': True,

    # Embedded dashboards
    'EMBEDDED_SUPERSET': True,

    # Row level security
    'ROW_LEVEL_SECURITY': True,

    # Chart features
    'ALLOW_FULL_CSV_EXPORT': True,
    'DYNAMIC_PLUGINS': False,
}

# SQL Lab Configuration
SQLLAB_TIMEOUT = int(os.getenv('SQLLAB_TIMEOUT', 300))
SQLLAB_ASYNC_TIME_LIMIT_SEC = int(os.getenv('SQLLAB_ASYNC_TIME_LIMIT_SEC', 600))
SQLLAB_VALIDATION_TIMEOUT = 10
SQLLAB_CTAS_NO_LIMIT = False
SQLLAB_SAVE_WARNING_MESSAGE = None

# Security
TALISMAN_ENABLED = os.getenv('TALISMAN_ENABLED', 'True').lower() == 'true'
TALISMAN_CONFIG = {
    'content_security_policy': None,
    'force_https': False,  # Set to True if behind HTTPS proxy
}

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'

# File upload configuration
UPLOAD_FOLDER = '/app/superset_home/uploads/'
UPLOAD_ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'parquet'}
CSV_TO_HIVE_UPLOAD_DIRECTORY = UPLOAD_FOLDER
EXCEL_EXTENSIONS = {'xlsx', 'xls'}
CSV_EXTENSIONS = {'csv', 'tsv', 'txt'}

# Image upload for dashboard thumbnails
IMG_UPLOAD_FOLDER = '/app/superset_home/thumbnails/'
IMG_UPLOAD_URL = '/static/thumbnails/'

# Email configuration (for reports and alerts)
SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
SMTP_STARTTLS = os.getenv('SMTP_STARTTLS', 'True').lower() == 'true'
SMTP_SSL = os.getenv('SMTP_SSL', 'False').lower() == 'true'
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_MAIL_FROM = os.getenv('SMTP_MAIL_FROM', 'superset@insightpulseai.net')

# WebDriver configuration for screenshots
WEBDRIVER_TYPE = 'chrome'
WEBDRIVER_OPTION_ARGS = [
    '--headless',
    '--disable-gpu',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-setuid-sandbox',
]

# Dashboard and chart export configuration
THUMBNAIL_SELENIUM_USER = 'admin'
THUMBNAIL_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
    'CACHE_KEY_PREFIX': 'thumbnail_',
    'CACHE_REDIS_HOST': os.getenv('REDIS_HOST', 'redis'),
    'CACHE_REDIS_PORT': int(os.getenv('REDIS_PORT', 6379)),
    'CACHE_REDIS_DB': 2,
}

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENABLE_TIME_ROTATE = True
FILENAME = '/app/superset_home/logs/superset.log'
ROLLOVER = 'midnight'
INTERVAL = 1
BACKUP_COUNT = 30

# API and CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*'],
}

# Branding
APP_NAME = 'InsightPulse AI - Business Intelligence'
APP_ICON = '/static/assets/images/insightpulse-logo.png'
APP_ICON_WIDTH = 126

# Custom CSS
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "insightpulse",
        "description": "InsightPulse AI color scheme",
        "label": "InsightPulse AI",
        "isDefault": True,
        "colors": [
            "#1f77b4",  # Blue
            "#ff7f0e",  # Orange
            "#2ca02c",  # Green
            "#d62728",  # Red
            "#9467bd",  # Purple
            "#8c564b",  # Brown
            "#e377c2",  # Pink
            "#7f7f7f",  # Gray
            "#bcbd22",  # Olive
            "#17becf",  # Cyan
        ],
    }
]

# Pre-configured Odoo datasource connection
# This will be imported automatically on first run
ODOO_DATABASE_URI = os.getenv(
    'ODOO_DATABASE_URI',
    f"postgresql://{os.getenv('DATABASE_USER', 'postgres')}:"
    f"{os.getenv('DATABASE_PASSWORD', 'postgres')}@postgres:5432/odoo"
)

# Custom SQL validation (optional)
# Prevents dangerous SQL operations in SQL Lab
PREVENT_UNSAFE_DEFAULT_URLS_ON_DATASET = True

# Map Mapbox configuration (if using map visualizations)
MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY', '')

# Row limit for charts
ROW_LIMIT = 50000
VIZ_ROW_LIMIT = 10000
SAMPLES_ROW_LIMIT = 1000

# Query results pagination
RESULTS_BACKEND = {
    'BACKEND': 'superset.result_backend.RedisResultsBackendConfig',
    'HOST': os.getenv('REDIS_HOST', 'redis'),
    'PORT': int(os.getenv('REDIS_PORT', 6379)),
    'DB': 3,
}

# Public role - for embedding dashboards
PUBLIC_ROLE_LIKE = 'Gamma'

# Alert & Report configuration
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
ALERT_MINIMUM_INTERVAL = 60  # seconds

# Custom OAuth configuration (optional)
# AUTH_TYPE = AUTH_OAUTH
# OAUTH_PROVIDERS = [...]

print("✅ Superset configuration loaded successfully")
print(f"📊 Database: {SQLALCHEMY_DATABASE_URI.split('@')[1] if '@' in SQLALCHEMY_DATABASE_URI else 'Not configured'}")
print(f"🔴 Redis: {os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', 6379)}")
print(f"📧 Email from: {SMTP_MAIL_FROM}")
