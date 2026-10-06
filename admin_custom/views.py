from django.db import models
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.models import User
from scholarships.models import Scholarship, StudyLevel, FundingType, Country, FieldOfStudy
from scholarships.serializers import ScholarshipSerializer
from .models import AdminLog
from .permissions import IsProjectAdmin
from .serializers import (
    AdminLogSerializer, AdminUserSerializer, AdminCreateUserSerializer,
    StudyLevelSerializer, FundingTypeSerializer,
    CountrySerializer, FieldOfStudySerializer,
)


def log_admin_action(admin_user, action, entity_type, entity_id=None, details=None):
    """Helper to create admin audit log."""
    AdminLog.objects.create(
        admin=admin_user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {}
    )


@api_view(['GET'])
@permission_classes([IsProjectAdmin])
def admin_dashboard(request):
    """Admin dashboard summary."""
    return Response({
        'total_users': User.objects.count(),
        'total_scholarships': Scholarship.objects.count(),
        'total_admins': User.objects.filter(models.Q(is_admin=True) | models.Q(is_staff=True)).count(),
        'total_study_levels': StudyLevel.objects.count(),
        'total_funding_types': FundingType.objects.count(),
        'total_countries': Country.objects.count(),
        'total_fields_of_study': FieldOfStudy.objects.count(),
    })


@api_view(['GET'])
@permission_classes([IsProjectAdmin])
def scholarship_list(request):
    """List all scholarships (admin only)."""
    scholarships = Scholarship.objects.select_related(
        'country', 'degree_level', 'field_of_study', 'funding_type'
    )
    return Response(ScholarshipSerializer(scholarships, many=True).data)


@api_view(['POST'])
@permission_classes([IsProjectAdmin])
def scholarship_create(request):
    """Create a scholarship (admin only)."""
    serializer = ScholarshipSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    scholarship = serializer.save()
    log_admin_action(request.user, 'create', 'scholarship', scholarship.id, {'title': scholarship.title})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsProjectAdmin])
def scholarship_update(request, pk):
    """Update a scholarship (admin only)."""
    try:
        scholarship = Scholarship.objects.get(pk=pk)
    except Scholarship.DoesNotExist:
        return Response({'error': 'Scholarship not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ScholarshipSerializer(scholarship, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    scholarship = serializer.save()
    log_admin_action(request.user, 'update', 'scholarship', scholarship.id)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsProjectAdmin])
def scholarship_delete(request, pk):
    """Delete a scholarship (admin only)."""
    try:
        scholarship = Scholarship.objects.get(pk=pk)
    except Scholarship.DoesNotExist:
        return Response({'error': 'Scholarship not found.'}, status=status.HTTP_404_NOT_FOUND)

    title = scholarship.title
    scholarship.delete()
    log_admin_action(request.user, 'delete', 'scholarship', pk, {'title': title})
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Generic taxonomy CRUD ──

TAXONOMY_MODELS = {
    'study-levels': (StudyLevel, StudyLevelSerializer, 'study_level'),
    'funding-types': (FundingType, FundingTypeSerializer, 'funding_type'),
    'countries': (Country, CountrySerializer, 'country'),
    'fields-of-study': (FieldOfStudy, FieldOfStudySerializer, 'field_of_study'),
}


def taxonomy_list(request, taxonomy_slug):
    """List all entries for a taxonomy type."""
    model, serializer_cls, _ = TAXONOMY_MODELS[taxonomy_slug]
    items = model.objects.all()
    return Response(serializer_cls(items, many=True).data)


def taxonomy_create(request, taxonomy_slug):
    """Create a new entry for a taxonomy type."""
    model, serializer_cls, entity_type = TAXONOMY_MODELS[taxonomy_slug]
    serializer = serializer_cls(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    item = serializer.save()
    log_admin_action(request.user, 'create', entity_type, item.id, {'name': str(item)})
    return Response(serializer_cls(item).data, status=status.HTTP_201_CREATED)


def taxonomy_update(request, taxonomy_slug, pk):
    """Update an entry for a taxonomy type."""
    model, serializer_cls, entity_type = TAXONOMY_MODELS[taxonomy_slug]
    try:
        item = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = serializer_cls(item, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    item = serializer.save()
    log_admin_action(request.user, 'update', entity_type, item.id, {'name': str(item)})
    return Response(serializer_cls(item).data)


def taxonomy_delete(request, taxonomy_slug, pk):
    """Delete an entry for a taxonomy type."""
    model, _, entity_type = TAXONOMY_MODELS[taxonomy_slug]
    try:
        item = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    name = str(item)
    item.delete()
    log_admin_action(request.user, 'delete', entity_type, pk, {'name': name})
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsProjectAdmin])
def taxonomy_dispatch(request, taxonomy_slug, pk=None):
    """Route GET/POST/PUT/PATCH/DELETE to the right handler."""
    if taxonomy_slug not in TAXONOMY_MODELS:
        return Response({'error': 'Unknown taxonomy.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET' and pk is None:
        return taxonomy_list(request, taxonomy_slug)
    if request.method == 'POST' and pk is None:
        return taxonomy_create(request, taxonomy_slug)
    if request.method in ('PUT', 'PATCH') and pk is not None:
        return taxonomy_update(request, taxonomy_slug, pk)
    if request.method == 'DELETE' and pk is not None:
        return taxonomy_delete(request, taxonomy_slug, pk)

    return Response({'error': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([IsProjectAdmin])
def user_list(request):
    users = User.objects.all()
    return Response(AdminUserSerializer(users, many=True).data)


@api_view(['POST'])
@permission_classes([IsProjectAdmin])
def user_create(request):
    """Create a new user (admin or student)."""
    serializer = AdminCreateUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    log_admin_action(request.user, 'create', 'user', user.id, {
        'email': user.email,
        'is_admin': user.is_admin,
    })
    return Response(AdminUserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsProjectAdmin])
def user_update(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.pk == request.user.pk and request.data.get('is_active') is False:
        return Response({'error': 'You cannot deactivate your own account.'}, status=status.HTTP_400_BAD_REQUEST)

    if 'is_active' not in request.data:
        return Response({'error': 'Only is_active can be updated.'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = bool(request.data['is_active'])
    user.save(update_fields=['is_active'])
    log_admin_action(request.user, 'update', 'user', user.id, {'is_active': user.is_active})
    return Response(AdminUserSerializer(user).data)


@api_view(['GET'])
@permission_classes([IsProjectAdmin])
def audit_log_list(request):
    logs = AdminLog.objects.select_related('admin').all()[:100]
    return Response(AdminLogSerializer(logs, many=True).data)
