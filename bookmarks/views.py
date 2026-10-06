from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Bookmark
from .serializers import BookmarkSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bookmark_list(request):
    """List all bookmarks for current user."""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('scholarship')
    serializer = BookmarkSerializer(bookmarks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bookmark_add(request):
    """Add a scholarship bookmark."""
    scholarship_id = request.data.get('scholarship')
    if not scholarship_id:
        return Response({'error': 'Scholarship ID required.'}, status=status.HTTP_400_BAD_REQUEST)

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        scholarship_id=scholarship_id
    )
    if not created:
        return Response({'error': 'Already bookmarked.'}, status=status.HTTP_409_CONFLICT)

    return Response(BookmarkSerializer(bookmark).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bookmark_remove(request, scholarship_id):
    """Remove a scholarship bookmark."""
    deleted, _ = Bookmark.objects.filter(user=request.user, scholarship_id=scholarship_id).delete()
    if not deleted:
        return Response({'error': 'Bookmark not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)
