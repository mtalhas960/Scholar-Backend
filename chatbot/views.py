from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_send(request):
    """Send a message and get a bot response."""
    message_text = request.data.get('message', '').strip()
    session_id = request.data.get('session_id')

    if not message_text:
        return Response({'error': 'Message is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get or create session
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        session = ChatSession.objects.create(user=request.user)

    # Save user message
    ChatMessage.objects.create(session=session, sender_type='user', message_text=message_text)

    # TODO: Call Groq AI to generate response
    bot_response = "Thank you for your message. The AI chatbot is being implemented."

    # Save bot message
    ChatMessage.objects.create(session=session, sender_type='bot', message_text=bot_response)

    return Response({
        'session_id': session.id,
        'response': bot_response,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request, session_id):
    """Get chat history for a session."""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ChatSessionSerializer(session)
    return Response(serializer.data)
