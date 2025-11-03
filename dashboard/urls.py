from django.urls import path
from . import views

urlpatterns = [
    path('', views.authority_dashboard, name='authority_dashboard'),
    path('issue/<int:pk>/manage/', views.manage_issue, name='manage_issue'),
]