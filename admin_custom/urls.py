from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('scholarships/', views.scholarship_list, name='admin-scholarship-list'),
    path('scholarships/create/', views.scholarship_create, name='admin-scholarship-create'),
    path('scholarships/<int:pk>/', views.scholarship_update, name='admin-scholarship-update'),
    path('scholarships/<int:pk>/delete/', views.scholarship_delete, name='admin-scholarship-delete'),
    path('taxonomy/<str:taxonomy_slug>/', views.taxonomy_dispatch, name='admin-taxonomy-list'),
    path('taxonomy/<str:taxonomy_slug>/<int:pk>/', views.taxonomy_dispatch, name='admin-taxonomy-detail'),
    path('users/', views.user_list, name='admin-user-list'),
    path('users/create/', views.user_create, name='admin-user-create'),
    path('users/<int:pk>/', views.user_update, name='admin-user-update'),
    path('logs/', views.audit_log_list, name='admin-audit-log-list'),
]
