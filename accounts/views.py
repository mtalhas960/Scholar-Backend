from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .serializers import (
    ChangePasswordSerializer,
    CombinedProfileSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Register a new student account."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login with email and password."""
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(
        {
            "access": str(serializer.validated_data["access"]),
            "refresh": str(serializer.validated_data["refresh"]),
            "user": serializer.validated_data["user"],
        },
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout (client-side token removal)."""
    return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """Get current authenticated user."""
    return Response(UserSerializer(request.user).data)


@api_view(["GET", "PUT"])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get or update combined user + student profile."""
    # Ensure profile exists (admin users may not have one)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return Response(CombinedProfileSerializer(request.user).data)

    serializer = CombinedProfileSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """Change the authenticated user's password."""
    serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "Password changed successfully."})
