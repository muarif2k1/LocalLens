from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from issues.models import Issue, IssueCategory, IssueStatusUpdate

def is_authority(user):
    return user.is_authenticated and user.is_authority

@login_required
@user_passes_test(is_authority)
def authority_dashboard(request):
    # Filter issues by authority's ward/zone if set
    issues = Issue.objects.all()
    if request.user.ward:
        issues = issues.filter(ward=request.user.ward)
    if request.user.zone:
        issues = issues.filter(zone=request.user.zone)
    
    # Statistics
    total_issues = issues.count()
    pending = issues.filter(status='pending').count()
    in_progress = issues.filter(status='in_progress').count()
    resolved = issues.filter(status='resolved').count()
    
    # Average resolution time
    avg_resolution = Issue.objects.filter(
        status='resolved',
        resolved_at__isnull=False
    ).aggregate(
        avg_days=Avg(
            timezone.now() - F('resolved_at')
        )
    )
    
    # Issues by category with percentage calculation
    issues_by_category = list(issues.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    # Calculate percentages for pie chart
    category_total = sum(cat['count'] for cat in issues_by_category)
    for cat in issues_by_category:
        cat['percentage'] = (cat['count'] / category_total * 100) if category_total > 0 else 0
    
    # Recent issues
    recent_issues = issues.order_by('-created_at')[:10]
    
    # Most reported areas
    hot_spots = issues.values('ward', 'zone').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_issues': total_issues,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'avg_resolution': avg_resolution,
        'issues_by_category': issues_by_category,
        'recent_issues': recent_issues,
        'hot_spots': hot_spots,
    }
    
    return render(request, 'dashboard/authority_dashboard.html', context)

@login_required
@user_passes_test(is_authority)
def manage_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        
        if new_status in dict(Issue.STATUS_CHOICES):
            old_status = issue.status
            issue.status = new_status
            
            if new_status == 'resolved':
                issue.resolved_at = timezone.now()
            
            issue.save()
            
            # Create status update record
            IssueStatusUpdate.objects.create(
                issue=issue,
                changed_by=request.user,
                old_status=old_status,
                new_status=new_status,
                note=note
            )
            
            messages.success(request, 'Issue status updated successfully!')
            return redirect('authority_dashboard')
    
    return render(request, 'dashboard/manage_issue.html', {'issue': issue})
