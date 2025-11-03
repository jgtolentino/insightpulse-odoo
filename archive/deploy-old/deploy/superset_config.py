"""
Superset Configuration for InsightPulse Odoo Integration

This config file sets up Superset to work behind a reverse proxy (Caddy)
with the /superset path prefix and integrates with Odoo database.
"""

import os
from flask_appbuilder.security.manager import AUTH_DB

# Flask-AppBuilder Configuration
# ---------------------------------------------------------
# Your App secret key - change this to a random secret key for production
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "changeme_generate_random_secret_key_here")

# The SQLAlchemy connection string for the metadata database
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{os.environ.get('SUPERSET_POSTGRES_USER', 'superset')}:"
    f"{os.environ.get('SUPERSET_POSTGRES_PASSWORD', 'superset')}@"
    f"superset-db:5432/{os.environ.get('SUPERSET_POSTGRES_DB', 'superset')}"
)

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "True").lower() == "true"
WTF_CSRF_TIME_LIMIT = None

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = os.environ.get("MAPBOX_API_KEY", "")

# Configuration for reverse proxy
# ---------------------------------------------------------
# Set to /superset when running behind Caddy with path prefix
APPLICATION_ROOT = os.environ.get("APPLICATION_ROOT", "/superset")
PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")

# Enable HTTP headers for proxy
ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {
    "x_for": 1,
    "x_proto": 1,
    "x_host": 1,
    "x_prefix": 1,
}

# Cache Configuration
# ---------------------------------------------------------
CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": os.environ.get("REDIS_HOST", "superset-redis"),
    "CACHE_REDIS_PORT": int(os.environ.get("REDIS_PORT", "6379")),
    "CACHE_REDIS_DB": 0,
}

# Async Query Configuration
# ---------------------------------------------------------
RESULTS_BACKEND = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_results_",
    "CACHE_REDIS_URL": f"redis://{os.environ.get('REDIS_HOST', 'superset-redis')}:6379/1",
}

# Feature Flags
# ---------------------------------------------------------
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": os.environ.get("FEATURE_ENABLE_TEMPLATE_PROCESSING", "True").lower() == "true",
    "DASHBOARD_CROSS_FILTERS": os.environ.get("FEATURE_DASHBOARD_CROSS_FILTERS", "True").lower() == "true",
    "DASHBOARD_NATIVE_FILTERS": os.environ.get("FEATURE_DASHBOARD_NATIVE_FILTERS", "True").lower() == "true",
    "EMBEDDABLE_CHARTS": True,
    "SCHEDULED_QUERIES": True,
    "ALERT_REPORTS": True,
}

# Row Level Security
# ---------------------------------------------------------
# Enable RLS for multi-company support
ROW_LEVEL_SECURITY_ENABLED = True

# Authentication Configuration
# ---------------------------------------------------------
AUTH_TYPE = AUTH_DB
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Gamma"  # Default role for self-registered users

# Database Connections Configuration
# ---------------------------------------------------------
# Pre-configured Odoo database connection
ODOO_DATABASE_URI = (
    f"postgresql://{os.environ.get('ODOO_DB_USER', 'odoo')}:"
    f"{os.environ.get('ODOO_DB_PASSWORD', 'odoo')}@"
    f"{os.environ.get('ODOO_DB_HOST', 'odoo-db')}:"
    f"{os.environ.get('ODOO_DB_PORT', '5432')}/"
    f"{os.environ.get('ODOO_DB_NAME', 'odoo')}"
)

# Additional Configuration
# ---------------------------------------------------------
# Disable sample data loading
SUPERSET_LOAD_EXAMPLES = os.environ.get("SUPERSET_LOAD_EXAMPLES", "no").lower() in ["yes", "true", "1"]

# Set the default language
BABEL_DEFAULT_LOCALE = "en"

# Allow embedding dashboards in iframes (for Odoo integration)
HTTP_HEADERS = {
    "X-Frame-Options": "SAMEORIGIN",
}

# CSV/Excel Export Configuration
CSV_EXPORT = {
    "encoding": "utf-8",
}

# Increase SQL query timeout for large datasets
SQLLAB_TIMEOUT = 300  # 5 minutes
SUPERSET_WEBSERVER_TIMEOUT = 300

# Logging Configuration
# ---------------------------------------------------------
import logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

# Enable detailed error messages (disable in production)
SHOW_STACKTRACE = os.environ.get("SUPERSET_ENV", "production") != "production"
