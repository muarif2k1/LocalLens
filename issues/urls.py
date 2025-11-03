from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report_issue, name='report_issue'),
    path('issue/<int:pk>/', views.issue_detail, name='issue_detail'),
    path('map/', views.issue_map, name='issue_map'),
    path('issue/<int:pk>/upvote/', views.upvote_issue, name='upvote_issue'),
    path('issue/<int:pk>/affected/', views.mark_affected, name='mark_affected'),
]