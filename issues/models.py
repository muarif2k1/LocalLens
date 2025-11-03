from django.contrib.gis.db import models as gis_models
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class IssueCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Issue Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Issue(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('duplicate', 'Duplicate'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('authorities_only', 'Visible to Authorities Only'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(IssueCategory, on_delete=models.PROTECT, related_name='issues')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_issues')
    
    # Location data
    location = gis_models.PointField()
    address = models.CharField(max_length=500)
    ward = models.CharField(max_length=100, blank=True)
    zone = models.CharField(max_length=100, blank=True)
    
    # Media
    image = models.ImageField(upload_to='issue_images/%Y/%m/%d/')
    
    # Status and privacy
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    
    # Engagement metrics
    upvotes = models.IntegerField(default=0)
    
    # Duplicate handling
    is_duplicate = models.BooleanField(default=False)
    duplicate_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='duplicates')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def resolution_time(self):
        if self.resolved_at:
            return (self.resolved_at - self.created_at).days
        return None


class IssueUpvote(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='upvote_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['issue', 'user']
    
    def __str__(self):
        return f"{self.user.username} upvoted {self.issue.title}"


class IssueComment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.issue.title}"


class IssueStatusUpdate(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='status_updates')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.issue.title}: {self.old_status} → {self.new_status}"


class AffectedUser(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='affected_users')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['issue', 'user']
    
    def __str__(self):
        return f"{self.user.username} affected by {self.issue.title}"
