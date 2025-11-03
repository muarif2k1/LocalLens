from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm
from issues.models import Issue, IssueUpvote
from django.http import JsonResponse

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to LocalLens.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    reported_issues = user.reported_issues.all()[:5]
    # Now properly fetches upvoted issues
    upvoted_issue_ids = IssueUpvote.objects.filter(user=user).values_list('issue_id', flat=True)
    upvoted_issues = Issue.objects.filter(id__in=upvoted_issue_ids)[:5]
    # upvoted_issues = [upvote.issue for upvote in user.issueupvote_set.all()[:5]]
    
    context = {
        'user': user,
        'reported_issues': reported_issues,
        'upvoted_issues': upvoted_issues,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})

@login_required
def update_notification_settings(request):
    if request.method == 'POST':
        setting = request.POST.get('setting')
        value = request.POST.get('value') == 'true'
        
        if setting == 'emailNotif':
            request.user.email_notifications = value
        elif setting == 'smsNotif':
            request.user.sms_notifications = value
        
        request.user.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def my_issues(request):
    issues = request.user.reported_issues.all().order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(issues, 10)  # 10 issues per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'issues': page_obj,
        'total_count': issues.count(),
    }
    return render(request, 'users/my_issues.html', context)
