from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from .models import Issue, IssueCategory, IssueUpvote, IssueComment, AffectedUser
from .forms import IssueReportForm, IssueCommentForm, IssueFilterForm
from django.utils.safestring import mark_safe
import json

def home(request):
    recent_issues = Issue.objects.filter(privacy='public', is_duplicate=False)[:6]
    categories = IssueCategory.objects.annotate(issue_count=Count('issues'))
    stats = {
        'total_issues': Issue.objects.count(),
        'resolved_issues': Issue.objects.filter(status='resolved').count(),
        'pending_issues': Issue.objects.filter(status='pending').count(),
    }
    return render(request, 'issues/home.html', {
        'recent_issues': recent_issues,
        'categories': categories,
        'stats': stats,
    })


@login_required
def report_issue(request):
    if request.method == 'POST':
        form = IssueReportForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.reporter = request.user
            issue.save()
            messages.success(request, 'Issue reported successfully!')
            return redirect('issue_detail', pk=issue.pk)
    else:
        form = IssueReportForm()
    
    return render(request, 'issues/report_issue.html', {'form': form})


def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    # Check privacy
    if issue.privacy == 'authorities_only' and not request.user.is_authority:
        if request.user != issue.reporter:
            messages.error(request, 'You do not have permission to view this issue.')
            return redirect('home')
    
    comments = issue.comments.select_related('user')
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = IssueCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.issue = issue
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('issue_detail', pk=pk)
    else:
        comment_form = IssueCommentForm()
    
    user_upvoted = False
    user_affected = False
    if request.user.is_authenticated:
        user_upvoted = IssueUpvote.objects.filter(issue=issue, user=request.user).exists()
        user_affected = AffectedUser.objects.filter(issue=issue, user=request.user).exists()
    
    return render(request, 'issues/issue_detail.html', {
        'issue': issue,
        'comments': comments,
        'comment_form': comment_form,
        'user_upvoted': user_upvoted,
        'user_affected': user_affected,
    })


def issue_map(request):
    filter_form = IssueFilterForm(request.GET)
    issues = Issue.objects.filter(privacy='public', is_duplicate=False)

    if filter_form.is_valid():
        if filter_form.cleaned_data.get('category'):
            issues = issues.filter(category=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data.get('status'):
            issues = issues.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data.get('date_from'):
            issues = issues.filter(created_at__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data.get('date_to'):
            issues = issues.filter(created_at__lte=filter_form.cleaned_data['date_to'])

    # Convert to JSON manually
    issues_data = [
        {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "category_name": issue.category.name,
            "reporter_username": issue.reporter.username,
            "address": issue.address,
            "image": issue.image.url if issue.image else None,
            "status": issue.status,
            "lat": issue.location.y if issue.location else None,
            "lng": issue.location.x if issue.location else None,
            "upvote_count": issue.upvotes,
            "comment_count": issue.comments.count(),
            "created_at": issue.created_at.isoformat(),
        }
        for issue in issues
    ]

    return render(request, 'issues/issue_map.html', {
        'issues_json': mark_safe(json.dumps(issues_data)),
        'filter_form': filter_form,
    })


@login_required
def upvote_issue(request, pk):
    if request.method == 'POST':
        issue = get_object_or_404(Issue, pk=pk)
        upvote, created = IssueUpvote.objects.get_or_create(issue=issue, user=request.user)
        
        if not created:
            upvote.delete()
            issue.upvotes -= 1
            issue.save()
            return JsonResponse({'status': 'removed', 'upvotes': issue.upvotes})
        else:
            issue.upvotes += 1
            issue.save()
            return JsonResponse({'status': 'added', 'upvotes': issue.upvotes})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def mark_affected(request, pk):
    if request.method == 'POST':
        issue = get_object_or_404(Issue, pk=pk)
        affected, created = AffectedUser.objects.get_or_create(issue=issue, user=request.user)
        
        if not created:
            affected.delete()
            return JsonResponse({'status': 'removed', 'count': issue.affected_users.count()})
        else:
            return JsonResponse({'status': 'added', 'count': issue.affected_users.count()})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
