"""
Celery Application for Visual Compliance Agent RAG/CAG Workers
Handles knowledge graph ingestion, embedding generation, and validation
"""

from celery import Celery
from celery.schedules import crontab
import os

# Celery configuration
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create Celery application
app = Celery('visual_compliance')

# Configure Celery
app.conf.update(
    broker_url=broker_url,
    result_backend=result_backend,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task routing (different queues for different worker types)
    task_routes={
        'visual_compliance.tasks.ingest_*': {'queue': 'ingestion'},
        'visual_compliance.tasks.generate_embeddings': {'queue': 'embedding'},
        'visual_compliance.tasks.deduplicate_*': {'queue': 'embedding'},
        'visual_compliance.tasks.validate_*': {'queue': 'validation'},
    },

    # Task execution settings
    task_acks_late=True,  # Acknowledge after task completion
    worker_prefetch_multiplier=1,  # Take one task at a time
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # 9 minutes soft limit (warning)

    # Retry settings
    task_default_retry_delay=60,  # Wait 1 minute before retry
    task_max_retries=3,

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,

    # Worker settings
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,

    # Monitoring
    task_send_sent_event=True,
    worker_send_task_events=True,

    # Beat schedule (periodic tasks)
    beat_schedule={
        # Refresh knowledge graph daily at 2 AM UTC
        'refresh-knowledge-graph': {
            'task': 'visual_compliance.tasks.refresh_knowledge_graph',
            'schedule': crontab(hour=2, minute=0),
        },
        # Calculate quality scores every 6 hours
        'update-quality-scores': {
            'task': 'visual_compliance.tasks.update_quality_scores',
            'schedule': crontab(minute=0, hour='*/6'),
        },
        # Deduplicate guidelines weekly on Sunday at 3 AM
        'deduplicate-weekly': {
            'task': 'visual_compliance.tasks.deduplicate_guidelines',
            'schedule': crontab(day_of_week='sunday', hour=3, minute=0),
        },
    },
)

# Auto-discover tasks in visual_compliance.tasks module
app.autodiscover_tasks(['visual_compliance'])

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery is working"""
    print(f'Request: {self.request!r}')
    return {'status': 'ok', 'worker': self.request.hostname}


if __name__ == '__main__':
    app.start()
