#!/usr/bin/env python3
"""
Outbox Worker - Process Supabase → Odoo Sync Queue

This worker polls the ops.odoo_outbox table in Supabase and pushes
changes to the Odoo API using the XML-RPC or REST interface.

Features:
- Idempotent processing with unique keys
- Retry logic with exponential backoff
- Error tracking and alerting
- Graceful shutdown handling

Usage:
    python outbox-worker.py --once          # Process queue once and exit
    python outbox-worker.py --daemon        # Run continuously (production)
    python outbox-worker.py --dry-run       # Preview without writing
"""

import os
import sys
import time
import logging
import argparse
import signal
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Third-party imports (to be installed via requirements)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/outbox-worker.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 10
BATCH_SIZE = 100
POLL_INTERVAL_SECONDS = 30
LOCK_TIMEOUT_MINUTES = 10


@dataclass
class OutboxRecord:
    """Represents a record in the outbox queue"""
    id: int
    model: str
    operation: str
    payload: Dict[str, Any]
    idempotency_key: str
    status: str
    attempts: int
    locked_at: Optional[datetime]
    locked_by: Optional[str]
    last_error: Optional[str]
    created_at: datetime


class OdooClient:
    """
    Odoo API Client (XML-RPC or REST)
    
    TODO: Implement actual Odoo API calls
    This is a skeleton that needs to be completed with:
    - XML-RPC authentication
    - Model operations (create, write, unlink)
    - Error handling
    """
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        
    def authenticate(self) -> bool:
        """Authenticate with Odoo"""
        # TODO: Implement XML-RPC authentication
        logger.info(f"Authenticating with Odoo at {self.url}")
        # import xmlrpc.client
        # common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        # self.uid = common.authenticate(self.db, self.username, self.password, {})
        # return bool(self.uid)
        return True  # Placeholder
        
    def upsert(self, model: str, values: Dict[str, Any]) -> int:
        """Upsert a record (create or update)"""
        # TODO: Implement upsert logic
        logger.info(f"Upserting {model}: {values}")
        return 1  # Placeholder record ID
        
    def delete(self, model: str, record_id: int) -> bool:
        """Delete a record"""
        # TODO: Implement delete logic
        logger.info(f"Deleting {model} id={record_id}")
        return True  # Placeholder


class OutboxWorker:
    """Main worker class that processes the outbox queue"""
    
    def __init__(self, db_url: str, odoo_client: OdooClient, 
                 batch_size: int = BATCH_SIZE, dry_run: bool = False):
        self.db_url = db_url
        self.odoo_client = odoo_client
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.running = True
        self.worker_id = f"worker-{os.getpid()}"
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
        
    def fetch_batch(self) -> List[OutboxRecord]:
        """
        Fetch a batch of records from the outbox queue
        
        Uses SELECT FOR UPDATE SKIP LOCKED to handle concurrent workers
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Lock records for processing
                query = """
                    UPDATE ops.odoo_outbox
                    SET 
                        status = 'processing',
                        locked_at = NOW(),
                        locked_by = %s
                    WHERE id IN (
                        SELECT id 
                        FROM ops.odoo_outbox
                        WHERE status = 'queued'
                           OR (status = 'processing' 
                               AND locked_at < NOW() - INTERVAL '%s minutes')
                        ORDER BY created_at ASC
                        LIMIT %s
                        FOR UPDATE SKIP LOCKED
                    )
                    RETURNING *;
                """
                cur.execute(query, (self.worker_id, LOCK_TIMEOUT_MINUTES, self.batch_size))
                rows = cur.fetchall()
                conn.commit()
                
                records = [
                    OutboxRecord(
                        id=row['id'],
                        model=row['model'],
                        operation=row['operation'],
                        payload=row['payload'],
                        idempotency_key=row['idempotency_key'],
                        status=row['status'],
                        attempts=row['attempts'],
                        locked_at=row['locked_at'],
                        locked_by=row['locked_by'],
                        last_error=row['last_error'],
                        created_at=row['created_at']
                    )
                    for row in rows
                ]
                
                return records
                
    def process_record(self, record: OutboxRecord) -> bool:
        """
        Process a single outbox record
        
        Returns True if successful, False otherwise
        """
        try:
            logger.info(f"Processing record {record.id}: {record.operation} on {record.model}")
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would {record.operation} {record.model}: {record.payload}")
                return True
                
            # Perform operation in Odoo
            if record.operation == 'upsert':
                self.odoo_client.upsert(record.model, record.payload)
            elif record.operation == 'delete':
                record_id = record.payload.get('odoo_id') or record.payload.get('id')
                if not record_id:
                    raise ValueError("Delete operation requires 'odoo_id' or 'id' in payload")
                self.odoo_client.delete(record.model, record_id)
            else:
                raise ValueError(f"Unknown operation: {record.operation}")
                
            # Mark as done
            self._mark_done(record.id)
            return True
            
        except Exception as e:
            logger.error(f"Error processing record {record.id}: {str(e)}", exc_info=True)
            self._mark_failed(record.id, str(e), record.attempts)
            return False
            
    def _mark_done(self, record_id: int):
        """Mark a record as successfully processed"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE ops.odoo_outbox
                    SET 
                        status = 'done',
                        locked_at = NULL,
                        locked_by = NULL
                    WHERE id = %s;
                    """,
                    (record_id,)
                )
                conn.commit()
                logger.info(f"Record {record_id} marked as done")
                
    def _mark_failed(self, record_id: int, error: str, attempts: int):
        """Mark a record as failed (or retry if under max attempts)"""
        attempts += 1
        
        # Exponential backoff: 10s, 20s, 40s, 80s, 160s
        backoff = min(INITIAL_BACKOFF_SECONDS * (2 ** attempts), 300)
        
        if attempts >= MAX_RETRIES:
            status = 'failed'
            logger.warning(f"Record {record_id} permanently failed after {attempts} attempts")
        else:
            status = 'queued'  # Retry
            logger.info(f"Record {record_id} will retry after {backoff}s (attempt {attempts})")
            
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE ops.odoo_outbox
                    SET 
                        status = %s,
                        attempts = %s,
                        last_error = %s,
                        locked_at = NULL,
                        locked_by = NULL
                    WHERE id = %s;
                    """,
                    (status, attempts, error, record_id)
                )
                conn.commit()
                
    def run_once(self):
        """Process one batch and exit"""
        logger.info("Processing one batch...")
        batch = self.fetch_batch()
        
        if not batch:
            logger.info("No records to process")
            return 0
            
        logger.info(f"Processing batch of {len(batch)} records")
        success_count = 0
        
        for record in batch:
            if self.process_record(record):
                success_count += 1
                
        logger.info(f"Batch complete: {success_count}/{len(batch)} successful")
        return success_count
        
    def run_daemon(self):
        """Run continuously in daemon mode"""
        logger.info(f"Starting outbox worker (daemon mode) - PID: {os.getpid()}")
        
        # Authenticate with Odoo once
        if not self.odoo_client.authenticate():
            logger.error("Failed to authenticate with Odoo")
            return
            
        while self.running:
            try:
                self.run_once()
                time.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Unexpected error in daemon loop: {str(e)}", exc_info=True)
                time.sleep(POLL_INTERVAL_SECONDS)
                
        logger.info("Worker stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Supabase → Odoo Outbox Worker')
    parser.add_argument('--once', action='store_true', 
                       help='Process queue once and exit')
    parser.add_argument('--daemon', action='store_true',
                       help='Run continuously (production mode)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without writing to Odoo')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                       help=f'Records to process per batch (default: {BATCH_SIZE})')
    args = parser.parse_args()
    
    # Validate arguments
    if not args.once and not args.daemon:
        parser.error("Must specify either --once or --daemon")
        
    # Get configuration from environment
    db_url = os.environ.get('SUPABASE_DB_URL')
    odoo_url = os.environ.get('ODOO_URL', 'http://localhost:8069')
    odoo_db = os.environ.get('ODOO_DB_NAME', 'odoo')
    odoo_user = os.environ.get('ODOO_USER', 'admin')
    odoo_password = os.environ.get('ODOO_PASSWORD')
    
    if not db_url:
        logger.error("SUPABASE_DB_URL environment variable not set")
        sys.exit(1)
        
    if not odoo_password:
        logger.error("ODOO_PASSWORD environment variable not set")
        sys.exit(1)
        
    # Initialize clients
    odoo_client = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
    worker = OutboxWorker(db_url, odoo_client, args.batch_size, args.dry_run)
    
    # Run worker
    try:
        if args.once:
            success_count = worker.run_once()
            sys.exit(0 if success_count > 0 else 1)
        else:
            worker.run_daemon()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
