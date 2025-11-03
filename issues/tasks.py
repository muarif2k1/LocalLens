from celery import shared_task
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Issue
from users.models import CustomUser

@shared_task
def send_status_update_email(issue_id, old_status, new_status):
    try:
        issue = Issue.objects.get(id=issue_id)
        if issue.reporter.email_notifications:
            subject = f'Issue Update: {issue.title}'
            message = f'''
            Your reported issue has been updated:
            
            Issue: {issue.title}
            Status changed from: {old_status} to {new_status}
            
            View details: {settings.SITE_URL}/issue/{issue.id}/
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [issue.reporter.email],
                fail_silently=False,
            )
    except Issue.DoesNotExist:
        pass


@shared_task
def notify_affected_users(issue_id):
    try:
        issue = Issue.objects.get(id=issue_id)
        affected_users = issue.affected_users.select_related('user')
        
        email_list = []
        for affected in affected_users:
            if affected.user.email_notifications:
                subject = f'Issue Resolved: {issue.title}'
                message = f'''
                An issue you marked as affecting you has been resolved:
                
                Issue: {issue.title}
                Resolved on: {issue.resolved_at}
                
                View details: {settings.SITE_URL}/issue/{issue.id}/
                '''
                email_list.append((
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [affected.user.email]
                ))
        
        if email_list:
            send_mass_mail(email_list, fail_silently=False)
    except Issue.DoesNotExist:
        pass


@shared_task
def send_daily_digest():
    # Send daily digest to authorities
    authorities = CustomUser.objects.filter(
        user_type__in=['authority', 'admin'],
        email_notifications=True
    )
    
    yesterday = timezone.now() - timedelta(days=1)
    
    for authority in authorities:
        issues = Issue.objects.filter(created_at__gte=yesterday)
        
        if authority.ward:
            issues = issues.filter(ward=authority.ward)
        if authority.zone:
            issues = issues.filter(zone=authority.zone)
        
        if issues.exists():
            subject = f'Daily Digest - {issues.count()} New Issues'
            message = f'''
            Hello {authority.username},
            
            Here's your daily digest:
            
            New Issues: {issues.count()}
            Pending: {issues.filter(status='pending').count()}
            In Progress: {issues.filter(status='in_progress').count()}
            
            View dashboard: {settings.SITE_URL}/dashboard/
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [authority.email],
                fail_silently=False,
            )


@shared_task
def send_new_issue_notification(issue_id):
    try:
        issue = Issue.objects.get(id=issue_id)
        
        # Notify relevant authorities
        authorities = CustomUser.objects.filter(
            user_type__in=['authority', 'admin'],
            email_notifications=True
        )
        
        if issue.ward:
            authorities = authorities.filter(ward=issue.ward)
        if issue.zone:
            authorities = authorities.filter(zone=issue.zone)
        
        email_list = []
        for authority in authorities:
            subject = f'New Issue Reported: {issue.title}'
            message = f'''
            A new issue has been reported in your jurisdiction:
            
            Title: {issue.title}
            Category: {issue.category.name}
            Location: {issue.address}
            
            View details: {settings.SITE_URL}/issue/{issue.id}/
            '''
            email_list.append((
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [authority.email]
            ))
        
        if email_list:
            send_mass_mail(email_list, fail_silently=False)
    except Issue.DoesNotExist:
        pass
