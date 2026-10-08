from collections import Counter
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.models import Student, Teacher, TeacherStudent
from apps.tests_app.models import TestResult, StudentAnswer
from apps.recommendations.models import StudentRecommendation


class ClassReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            teacher = request.user.teacher_profile
        except Exception:
            return Response({'detail': 'Доступ только для учителей.'}, status=status.HTTP_403_FORBIDDEN)

        grade = request.query_params.get('grade')

        linked_ids = list(
            TeacherStudent.objects
            .filter(teacher=teacher)
            .values_list('student_id', flat=True)
        )
        students_qs = Student.objects.filter(student_id__in=linked_ids)
        if grade:
            students_qs = students_qs.filter(grade=grade)

        student_ids = list(students_qs.values_list('student_id', flat=True))
        total_students = len(student_ids)

        # Студенты, завершившие хотя бы один тест
        tested_ids = set(
            TestResult.objects
            .filter(student_id__in=student_ids, status=TestResult.STATUS_COMPLETED)
            .values_list('student_id', flat=True)
        )
        students_tested = len(tested_ids)

        # Топ профессий по рекомендациям для класса (считаем уникальных учеников)
        recommendations = (
            StudentRecommendation.objects
            .filter(student_id__in=student_ids, recommendation_level=1)
            .select_related('profession')
        )
        profession_counter = Counter(r.profession.name for r in recommendations)
        top_professions = [
            {'name': name, 'count': count}
            for name, count in profession_counter.most_common(10)
        ]

        # Распределение категорий (Holland) — упрощённо по category профессий
        category_counter = Counter(r.profession.category for r in recommendations)

        return Response({
            'grade': grade,
            'total_students': total_students,
            'students_tested': students_tested,
            'holland_distribution': dict(category_counter),
            'top_professions': top_professions,
        })


class StudentListReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            teacher = request.user.teacher_profile
        except Exception:
            return Response({'detail': 'Доступ только для учителей.'}, status=status.HTTP_403_FORBIDDEN)

        grade = request.query_params.get('grade')
        linked_ids = list(
            TeacherStudent.objects
            .filter(teacher=teacher)
            .values_list('student_id', flat=True)
        )
        students_qs = Student.objects.filter(student_id__in=linked_ids)
        if grade:
            students_qs = students_qs.filter(grade=grade)

        result = []
        for s in students_qs.order_by('last_name', 'first_name'):
            completed = (
                TestResult.objects
                .filter(student=s, status=TestResult.STATUS_COMPLETED)
                .select_related('test')
                .order_by('test__task_number')
            )
            recs = (
                StudentRecommendation.objects
                .filter(student=s)
                .select_related('profession')
                .order_by('-match_percentage')[:3]
            )
            result.append({
                'student_id': s.student_id,
                'full_name': f'{s.last_name} {s.first_name}',
                'grade': s.grade,
                'email': s.email,
                'completed_tests': [
                    {'test_id': r.test.test_id, 'result_id': r.result_id,
                     'name': r.test.name, 'task_number': r.test.task_number}
                    for r in completed
                ],
                'top_recommendations': [
                    {'name': r.profession.name, 'match_percentage': float(r.match_percentage)}
                    for r in recs
                ],
            })
        return Response(result)


class StudentDetailReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        try:
            teacher = request.user.teacher_profile
        except Exception:
            return Response({'detail': 'Доступ только для учителей.'}, status=status.HTTP_403_FORBIDDEN)

        linked = TeacherStudent.objects.filter(teacher=teacher, student_id=student_id).exists()
        if not linked:
            return Response({'detail': 'Ученик не найден в вашем списке.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({'detail': 'Ученик не найден.'}, status=status.HTTP_404_NOT_FOUND)

        results = (
            TestResult.objects
            .filter(student=student, status=TestResult.STATUS_COMPLETED)
            .select_related('test')
            .order_by('test__task_number')
        )

        tests_data = []
        for r in results:
            answers = StudentAnswer.objects.filter(
                student=student, question__test=r.test
            ).select_related('option')
            scores = {'people': 0, 'intellectual': 0, 'practical': 0,
                      'aesthetic': 0, 'physical': 0, 'administrative': 0}
            for ans in answers:
                if ans.option:
                    scores['people'] += ans.option.weight_people
                    scores['intellectual'] += ans.option.weight_intellectual
                    scores['practical'] += ans.option.weight_practical
                    scores['aesthetic'] += ans.option.weight_aesthetic
                    scores['physical'] += ans.option.weight_physical
                    scores['administrative'] += ans.option.weight_administrative
            tests_data.append({
                'result_id': r.result_id,
                'test_name': r.test.name,
                'task_number': r.test.task_number,
                'test_type': r.test.test_type,
                'completion_date': r.completion_date,
                'scores': scores,
                'total_score': sum(scores.values()),
            })

        recs = (
            StudentRecommendation.objects
            .filter(student=student)
            .select_related('profession')
            .order_by('-match_percentage')
        )

        return Response({
            'student_id': student.student_id,
            'full_name': f'{student.last_name} {student.first_name}',
            'grade': student.grade,
            'email': student.email,
            'tests': tests_data,
            'global_recommendations': [
                {
                    'name': r.profession.name,
                    'match_percentage': float(r.match_percentage),
                    'level_label': {1: 'Высокое', 2: 'Среднее', 3: 'Низкое'}.get(r.recommendation_level, ''),
                }
                for r in recs
            ],
        })
