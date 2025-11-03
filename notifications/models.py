from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('issue_created', 'Issue Created'),
        ('issue_updated', 'Issue Updated'),
        ('issue_resolved', 'Issue Resolved'),
        ('comment_added', 'Comment Added'),
        ('upvote_received', 'Upvote Received'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preference'
    )
    
    email_on_issue_update = models.BooleanField(default=True)
    email_on_comment = models.BooleanField(default=True)
    email_on_resolution = models.BooleanField(default=True)
    
    push_on_issue_update = models.BooleanField(default=True)
    push_on_comment = models.BooleanField(default=False)
    push_on_resolution = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Notification Preferences - {self.user.username}"
