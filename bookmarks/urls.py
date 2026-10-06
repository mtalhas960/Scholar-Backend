from django.urls import path
from . import views

urlpatterns = [
    path('', views.bookmark_list, name='bookmark-list'),
    path('add/', views.bookmark_add, name='bookmark-add'),
    path('<int:scholarship_id>/', views.bookmark_remove, name='bookmark-remove'),
]
