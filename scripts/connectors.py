#!/usr/bin/env python3
"""
Odoo Connector Functions

This module provides connector functions for Odoo RPC, Supabase SQL, and Superset API.
These can be used standalone or imported into other scripts.

Usage:
    from connectors import odoo_rpc_call, supabase_sql, superset_api

    # Odoo RPC
    orders = odoo_rpc_call(
        url='http://localhost:8069',
        db='odoo',
        username='admin',
        password='admin',
        model='sale.order',
        method='search_read',
        args=[[('state', '=', 'sale')], ['name', 'amount_total']]
    )

    # Supabase SQL
    results = supabase_sql(
        connection_string='postgresql://user:pass@host:5432/db',
        query='SELECT * FROM vw_sales_kpi_day'
    )

    # Superset API
    dashboards = superset_api(
        base_url='https://superset.example.com',
        endpoint='/api/v1/dashboard/',
        auth_token='Bearer xxx'
    )
"""

import logging
import xmlrpc.client
from typing import Any, Dict, List, Optional, Union

import psycopg2
import psycopg2.extras
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def odoo_rpc_call(
    url: str,
    db: str,
    username: str,
    password: str,
    model: str,
    method: str,
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
) -> Any:
    """
    Execute RPC call to Odoo External API

    Args:
        url: Odoo server URL (e.g., 'http://localhost:8069')
        db: Database name
        username: User login
        password: User password or API key
        model: Model name (e.g., 'sale.order')
        method: Method to call (e.g., 'search_read')
        args: Positional arguments for the method
        kwargs: Keyword arguments for the method

    Returns:
        Result from the RPC call

    Example:
        # Search and read sale orders
        orders = odoo_rpc_call(
            url='http://localhost:8069',
            db='odoo',
            username='admin',
            password='admin',
            model='sale.order',
            method='search_read',
            args=[
                [('state', 'in', ['sale', 'done'])],  # domain
                ['name', 'date_order', 'amount_total']  # fields
            ]
        )

        # Create a new record
        new_id = odoo_rpc_call(
            url='http://localhost:8069',
            db='odoo',
            username='admin',
            password='admin',
            model='res.partner',
            method='create',
            args=[{
                'name': 'New Customer',
                'email': 'customer@example.com'
            }]
        )
    """
    args = args or []
    kwargs = kwargs or {}

    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})

        if not uid:
            raise ValueError(
                f"Authentication failed for user '{username}' on database '{db}'"
            )

        logger.info(f"Authenticated as user ID: {uid}")

        # Execute method
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        result = models.execute_kw(db, uid, password, model, method, args, kwargs)

        logger.info(f"Successfully executed {model}.{method}")
        return result

    except xmlrpc.client.Fault as e:
        logger.error(f"XML-RPC Fault: {e.faultCode} - {e.faultString}")
        raise
    except Exception as e:
        logger.error(f"Error in odoo_rpc_call: {e}")
        raise


def supabase_sql(
    connection_string: str,
    query: str,
    params: Optional[tuple] = None,
    fetch_mode: str = "all",
) -> Union[List[Dict], Dict, None]:
    """
    Execute SQL query against Supabase (PostgreSQL) database

    Args:
        connection_string: PostgreSQL connection string
                          (e.g., 'postgresql://user:pass@host:5432/db')
        query: SQL query to execute
        params: Query parameters (for parameterized queries)
        fetch_mode: 'all', 'one', or 'none'

    Returns:
        Query results as list of dictionaries (fetch_mode='all'),
        single dictionary (fetch_mode='one'),
        or None (fetch_mode='none')

    Example:
        # Fetch all sales metrics
        metrics = supabase_sql(
            connection_string='postgresql://user:pass@host:5432/odoo',
            query='''
                SELECT
                    date_trunc('month', date_order) as month,
                    SUM(amount_total) as revenue
                FROM sale_order
                WHERE state IN ('sale', 'done')
                GROUP BY month
                ORDER BY month DESC
                LIMIT 12
            '''
        )

        # Parameterized query
        orders = supabase_sql(
            connection_string='postgresql://user:pass@host:5432/odoo',
            query='SELECT * FROM sale_order WHERE partner_id = %s',
            params=(123,)
        )
    """
    conn = None
    cursor = None

    try:
        # Connect to database
        logger.info(f"Connecting to PostgreSQL database...")
        conn = psycopg2.connect(connection_string)

        # Use RealDictCursor to get results as dictionaries
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Execute query
        logger.info(f"Executing query...")
        cursor.execute(query, params)

        # Fetch results based on mode
        if fetch_mode == "all":
            results = cursor.fetchall()
            logger.info(f"Fetched {len(results)} rows")
            return [dict(row) for row in results]
        elif fetch_mode == "one":
            result = cursor.fetchone()
            if result:
                logger.info(f"Fetched 1 row")
                return dict(result)
            return None
        else:  # fetch_mode == 'none'
            conn.commit()
            logger.info(f"Query executed (no fetch)")
            return None

    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Error in supabase_sql: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Database connection closed")


def superset_api(
    base_url: str,
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    auth_token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Union[Dict, List]:
    """
    Interact with Apache Superset REST API

    Args:
        base_url: Superset base URL (e.g., 'https://superset.example.com')
        endpoint: API endpoint (e.g., '/api/v1/dashboard/')
        method: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
        data: Request body data (for POST/PUT)
        auth_token: Bearer token for authentication
        username: Username for login authentication
        password: Password for login authentication

    Returns:
        API response as dictionary or list

    Example:
        # Login and get access token
        login_response = superset_api(
            base_url='https://superset.example.com',
            endpoint='/api/v1/security/login',
            method='POST',
            data={
                'username': 'admin',
                'password': 'admin',
                'provider': 'db'
            }
        )
        access_token = login_response['access_token']

        # List dashboards
        dashboards = superset_api(
            base_url='https://superset.example.com',
            endpoint='/api/v1/dashboard/',
            auth_token=f'Bearer {access_token}'
        )

        # Create dataset
        dataset = superset_api(
            base_url='https://superset.example.com',
            endpoint='/api/v1/dataset/',
            method='POST',
            data={
                'database': 1,
                'table_name': 'vw_sales_kpi_day',
                'schema': 'public'
            },
            auth_token=f'Bearer {access_token}'
        )
    """
    try:
        # Prepare headers
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Add authentication
        if auth_token:
            headers["Authorization"] = auth_token
        elif username and password:
            # Login to get token
            login_url = f"{base_url}/api/v1/security/login"
            login_data = {
                "username": username,
                "password": password,
                "provider": "db",
                "refresh": True,
            }

            logger.info(f"Logging in to Superset...")
            login_response = requests.post(login_url, json=login_data, headers=headers)
            login_response.raise_for_status()

            token_data = login_response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                raise ValueError("Failed to obtain access token")

            headers["Authorization"] = f"Bearer {access_token}"
            logger.info("Successfully authenticated")

        # Make API request
        url = f"{base_url}{endpoint}"
        logger.info(f"Making {method} request to {url}")

        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Check response
        response.raise_for_status()

        # Parse response
        if response.content:
            result = response.json()
            logger.info(f"Request successful")
            return result
        else:
            logger.info(f"Request successful (no content)")
            return {}

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        if hasattr(e.response, "text"):
            logger.error(f"Response: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in superset_api: {e}")
        raise


# Convenience functions for common operations


def odoo_search_read(
    url: str,
    db: str,
    username: str,
    password: str,
    model: str,
    domain: List = None,
    fields: List = None,
    limit: int = None,
    offset: int = None,
) -> List[Dict]:
    """
    Simplified search_read operation

    Example:
        partners = odoo_search_read(
            url='http://localhost:8069',
            db='odoo',
            username='admin',
            password='admin',
            model='res.partner',
            domain=[('customer_rank', '>', 0)],
            fields=['name', 'email', 'phone'],
            limit=100
        )
    """
    domain = domain or []
    fields = fields or []

    kwargs = {}
    if limit:
        kwargs["limit"] = limit
    if offset:
        kwargs["offset"] = offset

    return odoo_rpc_call(
        url=url,
        db=db,
        username=username,
        password=password,
        model=model,
        method="search_read",
        args=[domain, fields],
        kwargs=kwargs,
    )


def superset_get_csrf_token(base_url: str, auth_token: str) -> str:
    """
    Get CSRF token for Superset API operations

    Some Superset endpoints require CSRF token.
    """
    response = superset_api(
        base_url=base_url,
        endpoint="/api/v1/security/csrf_token/",
        method="GET",
        auth_token=auth_token,
    )
    return response.get("result")


def superset_refresh_dashboard(base_url: str, dashboard_id: int, auth_token: str):
    """
    Refresh a Superset dashboard cache
    """
    csrf_token = superset_get_csrf_token(base_url, auth_token)

    return superset_api(
        base_url=base_url,
        endpoint=f"/api/v1/dashboard/{dashboard_id}/cache",
        method="DELETE",
        auth_token=auth_token,
    )


if __name__ == "__main__":
    # Example usage
    pass

    print("Odoo Connector Functions")
    print("=" * 50)
    print("\nAvailable functions:")
    print("  - odoo_rpc_call()")
    print("  - supabase_sql()")
    print("  - superset_api()")
    print("\nImport this module to use these functions:")
    print("  from connectors import odoo_rpc_call, supabase_sql, superset_api")
    print("\nSee function docstrings for usage examples.")
