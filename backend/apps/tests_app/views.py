from django.db import IntegrityError
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Test, TestResult, StudentAnswer
from .serializers import TestListSerializer, TestDetailSerializer, TestResultSerializer, SubmitAnswerSerializer
from apps.users.models import StudentUser


def get_student(user):
    try:
        return user.student_profile.student
    except StudentUser.DoesNotExist:
        return None


class TestListView(generics.ListAPIView):
    queryset = Test.objects.all().order_by('task_number', 'test_id')
    serializer_class = TestListSerializer
    permission_classes = [permissions.IsAuthenticated]


class TestDetailView(generics.RetrieveAPIView):
    queryset = Test.objects.prefetch_related('questions__options')
    serializer_class = TestDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'test_id'


class SubmitAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        student = get_student(request.user)
        if not student:
            return Response({'detail': 'Только учащиеся могут отвечать на вопросы.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            StudentAnswer.objects.create(
                student=student,
                question=data['question'],
                option=data['option'],
                answer_text=data.get('answer_text', '') if data['option'] is None else (data['option'].option_text if data['option'] else ''),
            )
        except IntegrityError:
            return Response({'detail': 'Вы уже ответили на этот вопрос.'}, status=status.HTTP_400_BAD_REQUEST)

        test = data['question'].test
        result, _ = TestResult.objects.get_or_create(
            student=student,
            test=test,
            defaults={'status': TestResult.STATUS_IN_PROGRESS},
        )

        if result.status != TestResult.STATUS_COMPLETED:
            answered_count = StudentAnswer.objects.filter(
                student=student, question__test=test
            ).count()
            if answered_count >= test.questions_count:
                result.status = TestResult.STATUS_COMPLETED
                result.completion_date = timezone.now()
                result.save()
                from apps.recommendations.tasks import generate_recommendations
                generate_recommendations.delay(result.result_id)

        return Response({
            'detail': 'Ответ сохранён.',
            'test_completed': result.status == TestResult.STATUS_COMPLETED,
            'result_id': result.result_id,
        })


class MyTestResultsView(generics.ListAPIView):
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student = get_student(self.request.user)
        if not student:
            return TestResult.objects.none()
        return TestResult.objects.filter(student=student).select_related('test').order_by('-start_date')


class TestResultDetailView(generics.RetrieveAPIView):
    serializer_class = TestResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'result_id'

    def get_queryset(self):
        student = get_student(self.request.user)
        if not student:
            return TestResult.objects.none()
        return TestResult.objects.filter(student=student).select_related('test')


class ResultScoresView(APIView):
    """Returns the accumulated weight vector for a completed test result."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, result_id):
        student = get_student(request.user)
        if not student:
            return Response({'detail': 'Только учащиеся могут просматривать результаты.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            result = TestResult.objects.select_related('test').get(pk=result_id, student=student)
        except TestResult.DoesNotExist:
            return Response({'detail': 'Результат не найден.'}, status=status.HTTP_404_NOT_FOUND)

        answers = StudentAnswer.objects.filter(student=student, question__test=result.test).select_related('option')

        scores = {
            'people': 0, 'intellectual': 0, 'practical': 0,
            'aesthetic': 0, 'physical': 0, 'administrative': 0,
        }
        for answer in answers:
            if answer.option:
                scores['people'] += answer.option.weight_people
                scores['intellectual'] += answer.option.weight_intellectual
                scores['practical'] += answer.option.weight_practical
                scores['aesthetic'] += answer.option.weight_aesthetic
                scores['physical'] += answer.option.weight_physical
                scores['administrative'] += answer.option.weight_administrative

        return Response({'scores': scores, 'test_type': result.test.test_type})


class DeleteResultView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, result_id):
        student = get_student(request.user)
        if not student:
            return Response({'detail': 'Только учащиеся могут удалять результаты.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            result = TestResult.objects.get(pk=result_id, student=student)
        except TestResult.DoesNotExist:
            return Response({'detail': 'Результат не найден.'}, status=status.HTTP_404_NOT_FOUND)
        StudentAnswer.objects.filter(student=student, question__test=result.test).delete()
        result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResultAnswersView(APIView):
    """Returns student's text answers for reflection tests."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, result_id):
        student = get_student(request.user)
        if not student:
            return Response({'detail': 'Только учащиеся могут просматривать результаты.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            result = TestResult.objects.select_related('test').get(pk=result_id, student=student)
        except TestResult.DoesNotExist:
            return Response({'detail': 'Результат не найден.'}, status=status.HTTP_404_NOT_FOUND)

        answers = (
            StudentAnswer.objects
            .filter(student=student, question__test=result.test)
            .select_related('question')
            .order_by('question__question_order')
        )

        data = [
            {
                'question_text': a.question.question_text,
                'answer_text': a.answer_text or '',
            }
            for a in answers
        ]

        return Response({'answers': data, 'test_type': result.test.test_type})
