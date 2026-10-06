from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.ScholarshipViewSet, basename='scholarship')

urlpatterns = [
    path('taxonomy/', views.taxonomy_options, name='taxonomy-options'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('', include(router.urls)),
]
