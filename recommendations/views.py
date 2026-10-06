from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Recommendation
from .serializers import RecommendationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendation_list(request):
    """Get recommendations for current user."""
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.degree_level:
        return Response(
            {'error': 'Please complete your profile to get recommendations.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    recommendations = Recommendation.objects.filter(user=request.user).select_related('scholarship')
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)
