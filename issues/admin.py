from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import (
    IssueCategory, Issue, IssueUpvote, 
    IssueComment, IssueStatusUpdate, AffectedUser
)

@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Issue)
class IssueAdmin(OSMGeoAdmin):
    list_display = ['title', 'category', 'status', 'reporter', 'created_at', 'upvotes']
    list_filter = ['status', 'category', 'privacy', 'created_at']
    search_fields = ['title', 'description', 'address']
    readonly_fields = ['created_at', 'updated_at']
    
@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    list_display = ['issue', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comment', 'issue__title']

@admin.register(IssueStatusUpdate)
class IssueStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['issue', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
