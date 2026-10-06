from rest_framework import serializers

from accounts.models import User
from scholarships.models import StudyLevel, FundingType, Country, FieldOfStudy
from .models import AdminLog


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'is_admin',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = fields


class AdminLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source='admin.email', read_only=True)

    class Meta:
        model = AdminLog
        fields = ['id', 'admin_email', 'action', 'entity_type', 'entity_id', 'details', 'created_at']


class StudyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyLevel
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class FundingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingType
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'slug', 'flag', 'code']
        read_only_fields = ['slug']


class FieldOfStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOfStudy
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class AdminCreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")
    password = serializers.CharField(write_only=True, min_length=8)
    is_admin = serializers.BooleanField(default=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        if user.is_admin:
            user.is_staff = True
        user.save()
        return user