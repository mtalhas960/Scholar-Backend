from rest_framework import serializers
from .models import Scholarship, StudyLevel, FundingType, Country, FieldOfStudy


class StudyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyLevel
        fields = ['id', 'name', 'slug']


class FundingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingType
        fields = ['id', 'name', 'slug']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'slug', 'flag', 'code']


class FieldOfStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOfStudy
        fields = ['id', 'name', 'slug']


class ScholarshipSerializer(serializers.ModelSerializer):
    # Nested read-only representations
    country_detail = CountrySerializer(source='country', read_only=True)
    degree_level_detail = StudyLevelSerializer(source='degree_level', read_only=True)
    field_of_study_detail = FieldOfStudySerializer(source='field_of_study', read_only=True)
    funding_type_detail = FundingTypeSerializer(source='funding_type', read_only=True)

    class Meta:
        model = Scholarship
        fields = [
            'id',
            'slug',
            'title',
            'country',
            'country_detail',
            'degree_level',
            'degree_level_detail',
            'field_of_study',
            'field_of_study_detail',
            'funding_type',
            'funding_type_detail',
            'funding_amount',
            'deadline',
            'application_url',
            'image_url',
            'description',
            'eligibility_criteria',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
