# Superset Production Configuration for DigitalOcean App Platform
# Uses Supabase PostgreSQL as metadata database

import os
from cachelib.redis import RedisCache

# Database Configuration
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_DB')}"
)

# Redis Cache Configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300)),
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
    'CACHE_REDIS_PORT': int(os.getenv('REDIS_PORT', 6379)),
    'CACHE_REDIS_DB': int(os.getenv('REDIS_CELERY_DB', 0)),
}

# Data Cache Configuration
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': int(os.getenv('DATA_CACHE_DEFAULT_TIMEOUT', 3600)),
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
    'CACHE_REDIS_PORT': int(os.getenv('REDIS_PORT', 6379)),
    'CACHE_REDIS_DB': int(os.getenv('REDIS_RESULTS_DB', 1)),
}

# Security Configuration
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Database Engine Options (for PostgreSQL foreign key support)
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'connect_args': {
        'connect_timeout': 10,
        'options': '-c statement_timeout=60000'  # 60 second timeout
    }
}

# Ensure foreign keys are enforced
SQLALCHEMY_ECHO = False

# Webserver Configuration
SUPERSET_WEBSERVER_PROTOCOL = os.getenv('SUPERSET_WEBSERVER_PROTOCOL', 'https')
SUPERSET_WEBSERVER_PORT = int(os.getenv('SUPERSET_WEBSERVER_PORT', 8088))
ENABLE_PROXY_FIX = True

# Flask-WTF Configuration
WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = []
WTF_CSRF_TIME_LIMIT = None

# Logging Configuration
LOG_LEVEL = os.getenv('SUPERSET_LOG_LEVEL', 'WARNING').upper()

# Feature Flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
}

# Row Level Security
ROW_LEVEL_SECURITY = True

# Load Examples
SUPERSET_LOAD_EXAMPLES = os.getenv('SUPERSET_LOAD_EXAMPLES', 'no').lower() == 'yes'
