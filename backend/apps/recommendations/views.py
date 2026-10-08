from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ProfessionRecommendation, StudentRecommendation
from .serializers import RecommendationSerializer, StudentRecommendationSerializer
from apps.users.models import StudentUser
from apps.tests_app.models import TestResult


class MyRecommendationsView(generics.ListAPIView):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            student = self.request.user.student_profile.student
        except StudentUser.DoesNotExist:
            return ProfessionRecommendation.objects.none()

        return (
            ProfessionRecommendation.objects
            .filter(result__student=student)
            .select_related('profession')
            .order_by('-match_percentage')
        )


class ResultRecommendationsView(generics.ListAPIView):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        result_id = self.kwargs['result_id']
        try:
            student = self.request.user.student_profile.student
        except Exception:
            return ProfessionRecommendation.objects.none()

        return (
            ProfessionRecommendation.objects
            .filter(result_id=result_id, result__student=student)
            .select_related('profession')
            .order_by('-match_percentage')
        )


class StudentRecommendationsView(generics.ListAPIView):
    serializer_class = StudentRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            student = self.request.user.student_profile.student
        except Exception:
            return StudentRecommendation.objects.none()
        return StudentRecommendation.objects.filter(student=student).select_related('profession')
