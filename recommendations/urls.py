from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommendation_list, name='recommendation-list'),
]
