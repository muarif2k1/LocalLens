from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notification

@shared_task
def cleanup_old_notifications():
    # Delete read notifications older than 30 days
    threshold = timezone.now() - timedelta(days=30)
    deleted_count = Notification.objects.filter(
        is_read=True,
        created_at__lt=threshold
    ).delete()[0]
    
    return f"Deleted {deleted_count} old notifications"


@shared_task
def create_notification(recipient_id, notification_type, title, message, link=''):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        recipient = User.objects.get(id=recipient_id)
        Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
        return f"Notification created for {recipient.username}"
    except User.DoesNotExist:
        return "User not found"