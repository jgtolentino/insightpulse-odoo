#!/usr/bin/env python3
"""
Auto-heal database connection issues
Monitors PostgreSQL connections and auto-remediates when threshold exceeded
"""

import os
import sys
import time
import psycopg2
import subprocess
from datetime import datetime

MAX_CONNECTIONS_THRESHOLD = 0.9  # 90% of max_connections
IDLE_TIMEOUT_MINUTES = 5


def send_alert(message):
    """Send alert to monitoring system"""
    # Integration with alerting system (Slack, PagerDuty, etc.)
    print(f"🚨 ALERT: {message}")


def check_db_connections():
    """Monitor and auto-fix database connection issues"""
    db_host = os.getenv("PGHOST", "db")
    db_name = os.getenv("PGDATABASE", "odoo")
    db_user = os.getenv("PGUSER", "odoo")
    db_password = os.getenv("PGPASSWORD")

    if not db_password:
        print("❌ PGPASSWORD not set")
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        cur = conn.cursor()

        # Get current connections for this user
        cur.execute("""
            SELECT count(*)
            FROM pg_stat_activity
            WHERE usename = %s
        """, (db_user,))
        current = cur.fetchone()[0]

        # Get max connections
        cur.execute("SHOW max_connections;")
        max_conn = int(cur.fetchone()[0])

        usage = current / max_conn
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{timestamp}] DB connections: {current}/{max_conn} ({usage*100:.1f}%)")

        if usage > MAX_CONNECTIONS_THRESHOLD:
            print(f"⚠️  DB connections at critical level: {usage*100:.1f}% ({current}/{max_conn})")

            # Kill idle connections older than IDLE_TIMEOUT_MINUTES
            cur.execute(f"""
                SELECT pg_terminate_backend(pid), pid, state, state_change
                FROM pg_stat_activity
                WHERE usename = %s
                  AND state = 'idle'
                  AND state_change < now() - interval '{IDLE_TIMEOUT_MINUTES} minutes'
            """, (db_user,))

            killed = cur.rowcount
            print(f"✅ Killed {killed} idle connections (idle > {IDLE_TIMEOUT_MINUTES} min)")

            if killed > 0:
                # Log killed connections
                for row in cur.fetchall():
                    print(f"   Killed PID {row[1]}: {row[2]} since {row[3]}")

            # Re-check after killing idle connections
            cur.execute("""
                SELECT count(*)
                FROM pg_stat_activity
                WHERE usename = %s
            """, (db_user,))
            current_after = cur.fetchone()[0]
            usage_after = current_after / max_conn

            print(f"After cleanup: {current_after}/{max_conn} ({usage_after*100:.1f}%)")

            # If still critical after cleanup, restart Odoo
            if usage_after > MAX_CONNECTIONS_THRESHOLD:
                print("⚠️  Still at critical level - restarting Odoo to reset connection pool")
                subprocess.run(['docker-compose', 'restart', 'odoo'], check=False)
                print("✅ Odoo restarted")
                send_alert(f"Odoo restarted due to high DB connections: {usage_after*100:.1f}%")
            else:
                send_alert(f"DB connections auto-healed: {usage*100:.1f}% → {usage_after*100:.1f}%")
        else:
            print(f"✅ DB connections healthy")

        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        send_alert(f"DB connection check failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        send_alert(f"DB connection monitor error: {e}")
        return False


if __name__ == '__main__':
    check_db_connections()
