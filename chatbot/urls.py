from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.chat_send, name='chat-send'),
    path('history/<int:session_id>/', views.chat_history, name='chat-history'),
]
