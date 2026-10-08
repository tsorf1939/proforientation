from rest_framework import serializers
from .models import ProfessionRecommendation, StudentRecommendation
from apps.careers.serializers import ProfessionListSerializer

_LEVEL_LABELS = {1: 'Высокое совпадение', 2: 'Среднее совпадение', 3: 'Низкое совпадение'}


class RecommendationSerializer(serializers.ModelSerializer):
    profession = ProfessionListSerializer(read_only=True)
    level_label = serializers.SerializerMethodField()

    class Meta:
        model = ProfessionRecommendation
        fields = ['recommendation_id', 'profession', 'match_percentage', 'recommendation_level', 'level_label']

    def get_level_label(self, obj):
        return _LEVEL_LABELS.get(obj.recommendation_level, '')


class StudentRecommendationSerializer(serializers.ModelSerializer):
    profession = ProfessionListSerializer(read_only=True)
    level_label = serializers.SerializerMethodField()

    class Meta:
        model = StudentRecommendation
        fields = ['recommendation_id', 'profession', 'match_percentage',
                  'recommendation_level', 'level_label', 'updated_at']

    def get_level_label(self, obj):
        return _LEVEL_LABELS.get(obj.recommendation_level, '')
