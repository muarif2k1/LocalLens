from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('citizen', 'Citizen'),
        ('authority', 'Local Authority'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='citizen')
    phone_number = models.CharField(max_length=15, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    zone = models.CharField(max_length=100, blank=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_authority(self):
        return self.user_type in ['authority', 'admin']