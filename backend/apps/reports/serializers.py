from rest_framework import serializers
from apps.users.models import Student
from apps.recommendations.models import ProfessionRecommendation
from apps.tests_app.models import TestResult


class ClassReportSerializer(serializers.Serializer):
    grade = serializers.IntegerField()
    school_id = serializers.IntegerField()
    total_students = serializers.IntegerField()
    students_tested = serializers.IntegerField()
    holland_distribution = serializers.DictField()
    top_professions = serializers.ListField()
