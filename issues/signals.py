from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Issue, IssueStatusUpdate
from .tasks import (
    send_status_update_email, 
    notify_affected_users,
    send_new_issue_notification
)

@receiver(post_save, sender=Issue)
def issue_created(sender, instance, created, **kwargs):
    if created:
        # Send notifications to authorities
        send_new_issue_notification.delay(instance.id)


@receiver(pre_save, sender=Issue)
def track_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Issue.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Create status update record
                IssueStatusUpdate.objects.create(
                    issue=instance,
                    changed_by=instance.reporter,  # Should be set in view
                    old_status=old_instance.status,
                    new_status=instance.status
                )
                
                # Send notification
                send_status_update_email.delay(
                    instance.id,
                    old_instance.status,
                    instance.status
                )
                
                # If resolved, notify affected users
                if instance.status == 'resolved':
                    instance.resolved_at = timezone.now()
                    notify_affected_users.delay(instance.id)
        except Issue.DoesNotExist:
            pass