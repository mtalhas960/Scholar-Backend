from rest_framework import serializers
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    scholarship_title = serializers.CharField(source='scholarship.title', read_only=True)
    match_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ['id', 'scholarship', 'scholarship_title', 'score', 'rank', 'match_percentage', 'generated_at']
        read_only_fields = ['id', 'score', 'rank', 'generated_at']

    def get_match_percentage(self, obj):
        return round(obj.score * 100, 1)
