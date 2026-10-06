from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Profile
from scholarships.models import FieldOfStudy, FundingType, Country


class FieldOfStudyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOfStudy
        fields = ['id', 'name', 'slug']


class FundingTypeBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingType
        fields = ['id', 'name', 'slug']


class CountryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'slug', 'flag']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "is_admin", "is_staff", "is_superuser", "profile_photo", "date_joined"]
        read_only_fields = ["id", "is_admin", "is_staff", "is_superuser", "date_joined"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "degree_level", "field_of_study", "gpa", "nationality", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class CombinedProfileSerializer(serializers.ModelSerializer):
    """Serializes User fields + Profile fields together."""
    degree_level = serializers.CharField(source='profile.degree_level', required=False)
    field_of_study = serializers.PrimaryKeyRelatedField(
        many=True, queryset=FieldOfStudy.objects.all(),
        source='profile.field_of_study', required=False,
    )
    field_of_study_detail = FieldOfStudyBriefSerializer(source='profile.field_of_study', many=True, read_only=True)
    gpa = serializers.DecimalField(source='profile.gpa', max_digits=3, decimal_places=2, required=False, allow_null=True)
    nationality = serializers.CharField(source='profile.nationality', required=False)
    funding_preferences = serializers.PrimaryKeyRelatedField(
        many=True, queryset=FundingType.objects.all(),
        source='profile.funding_preferences', required=False,
    )
    funding_preferences_detail = FundingTypeBriefSerializer(source='profile.funding_preferences', many=True, read_only=True)
    preferred_countries = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Country.objects.all(),
        source='profile.preferred_countries', required=False,
    )
    preferred_countries_detail = CountryBriefSerializer(source='profile.preferred_countries', many=True, read_only=True)
    profile_updated_at = serializers.DateTimeField(source='profile.updated_at', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_admin', 'is_staff', 'profile_photo', 'date_joined',
            'degree_level', 'field_of_study', 'field_of_study_detail',
            'gpa', 'nationality',
            'funding_preferences', 'funding_preferences_detail',
            'preferred_countries', 'preferred_countries_detail',
            'profile_updated_at',
        ]
        read_only_fields = ['id', 'email', 'is_admin', 'is_staff', 'date_joined', 'profile_updated_at']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.profile
            m2m_fields = {}
            for attr, value in profile_data.items():
                field = profile._meta.get_field(attr)
                if field.many_to_many:
                    m2m_fields[attr] = value
                else:
                    setattr(profile, attr, value)
            profile.save()
            for attr, value in m2m_fields.items():
                getattr(profile, attr).set(value)
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends TokenObtainPair to include user data in the response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
