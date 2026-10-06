from rest_framework import serializers
from .models import Bookmark
from scholarships.serializers import ScholarshipSerializer


class BookmarkSerializer(serializers.ModelSerializer):
    scholarship_title = serializers.CharField(source='scholarship.title', read_only=True)
    scholarship_detail = ScholarshipSerializer(source='scholarship', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'scholarship', 'scholarship_title', 'scholarship_detail', 'created_at']
        read_only_fields = ['id', 'created_at']
