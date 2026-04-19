# OrderManagement/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_admin_email_task(self, order_id):
    # placeholder until Brevo is configured
    logger.info(f"[TODO] Admin email for order #{order_id}")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_customer_email_task(self, order_id):
    logger.info(f"[TODO] Customer email for order #{order_id}")


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def send_firebase_push_task(self, order_id):
    logger.info(f"[TODO] Firebase push for order #{order_id}")