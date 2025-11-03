from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 
        'email', 
        'user_type', 
        'ward',
        'zone',
        'get_issues_count',
        'is_active',
        'date_joined'
    ]
    
    list_filter = [
        'user_type',
        'is_staff', 
        'is_active',
        'ward',
        'zone',
        'date_joined'
    ]
    
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name',
        'phone_number',
        'ward',
        'zone'
    ]
    
    fieldsets = (
        ('Login Information', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('User Type & Location', {
            'fields': ('user_type', 'ward', 'zone'),
            'description': 'Assign user role and location details'
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Login Information', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
        ('User Type & Location', {
            'fields': ('user_type', 'ward', 'zone')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active')
        }),
    )
    
    ordering = ['-date_joined']
    
    # Custom method to show issue count
    def get_issues_count(self, obj):
        return obj.reported_issues.count()
    get_issues_count.short_description = 'Issues Reported'
    
    # Optimize queries
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            issues_count=Count('reported_issues')
        )

# Customize admin site
admin.site.site_header = "LocalLens Administration"
admin.site.site_title = "LocalLens Admin Portal"
admin.site.index_title = "Welcome to LocalLens Admin"