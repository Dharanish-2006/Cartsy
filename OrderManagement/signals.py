import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from OrderManagement.utils.zoho import create_zoho_contact, create_zoho_deal

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def sync_order_to_zoho(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        create_zoho_contact(instance.user, order=instance)
        create_zoho_deal(instance)
        logger.info(f"Zoho sync success for Order #{instance.id}")
    except Exception as e:
        logger.error(f"Zoho sync failed for Order #{instance.id}: {e}")