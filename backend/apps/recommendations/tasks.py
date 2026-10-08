import numpy as np
from celery import shared_task
from django.db import transaction

RECOMMENDATION_TASK_NUMBERS = (12, 13, 14, 15)


@shared_task(bind=True, max_retries=3)
def generate_recommendations(self, result_id: int):
    """
    Генерирует рекомендации профессий на основе косинусного сходства.
    Запускается автоматически после завершения теста (сигнал post_save на TestResult).

    Алгоритм:
    1. Собираем ответы студента, суммируем веса по 6 категориям (Казакова)
    2. Для каждой профессии берём её вектор весов
    3. Вычисляем косинусное сходство между вектором студента и вектором профессии
    4. Сохраняем топ-5 профессий в ProfessionRecommendation
    """
    try:
        from apps.tests_app.models import TestResult, StudentAnswer
        from apps.careers.models import Profession, ProfessionTypeWeights
        from .models import ProfessionRecommendation

        result = TestResult.objects.select_related('student', 'test').get(pk=result_id)
        student = result.student
        test = result.test

        # Получаем все ответы студента для данного теста
        answers = (
            StudentAnswer.objects
            .filter(student=student, question__test=test)
            .select_related('option')
        )

        # Суммируем веса по 6 категориям
        student_vector = np.zeros(6)
        for answer in answers:
            if answer.option:
                student_vector[0] += answer.option.weight_people
                student_vector[1] += answer.option.weight_intellectual
                student_vector[2] += answer.option.weight_practical
                student_vector[3] += answer.option.weight_aesthetic
                student_vector[4] += answer.option.weight_physical
                student_vector[5] += answer.option.weight_administrative

        student_norm = np.linalg.norm(student_vector)

        # Получаем все профессии с весами
        professions_with_weights = ProfessionTypeWeights.objects.select_related('profession').all()

        scored = []
        for pw in professions_with_weights:
            prof_vector = np.array([
                pw.weight_people,
                pw.weight_intellectual,
                pw.weight_practical,
                pw.weight_aesthetic,
                pw.weight_physical,
                pw.weight_administrative,
            ], dtype=float)

            prof_norm = np.linalg.norm(prof_vector)

            if student_norm > 0 and prof_norm > 0:
                cosine_similarity = np.dot(student_vector, prof_vector) / (student_norm * prof_norm)
                match_pct = round(float(cosine_similarity) * 100, 2)
            else:
                match_pct = 0.0

            scored.append((pw.profession, match_pct))

        # Топ-5 по убыванию процента совпадения
        top5 = sorted(scored, key=lambda x: x[1], reverse=True)[:5]

        with transaction.atomic():
            # Удаляем старые рекомендации для этого результата
            ProfessionRecommendation.objects.filter(result=result).delete()

            for profession, match_pct in top5:
                ProfessionRecommendation.objects.create(
                    result=result,
                    profession=profession,
                    match_percentage=max(0.0, min(100.0, match_pct)),
                    # recommendation_level будет установлен триггером БД
                    recommendation_level=1 if match_pct >= 70 else (2 if match_pct >= 40 else 3),
                )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_student_recommendations(self, student_id: int):
    """
    Агрегирует ответы студента по заданиям 13–16 (ДДО, Холланд, Йовайша, Профпригодность)
    и вычисляет глобальные рекомендации профессий через косинусное сходство.
    Запускается только после завершения всех 4 заданий.
    """
    try:
        from apps.tests_app.models import StudentAnswer
        from apps.careers.models import ProfessionTypeWeights
        from .models import StudentRecommendation

        answers = (
            StudentAnswer.objects
            .filter(student_id=student_id, option__isnull=False,
                    question__test__task_number__in=RECOMMENDATION_TASK_NUMBERS)
            .select_related('option')
        )

        student_vector = np.zeros(6)
        for ans in answers:
            o = ans.option
            student_vector[0] += o.weight_people
            student_vector[1] += o.weight_intellectual
            student_vector[2] += o.weight_practical
            student_vector[3] += o.weight_aesthetic
            student_vector[4] += o.weight_physical
            student_vector[5] += o.weight_administrative

        student_norm = np.linalg.norm(student_vector)
        if student_norm == 0:
            return

        scored = []
        for pw in ProfessionTypeWeights.objects.select_related('profession').all():
            prof_vector = np.array([
                pw.weight_people, pw.weight_intellectual, pw.weight_practical,
                pw.weight_aesthetic, pw.weight_physical, pw.weight_administrative,
            ], dtype=float)
            prof_norm = np.linalg.norm(prof_vector)
            if prof_norm > 0:
                cos = np.dot(student_vector, prof_vector) / (student_norm * prof_norm)
                scored.append((pw.profession, round(float(cos) * 100, 2)))

        top5 = sorted(scored, key=lambda x: x[1], reverse=True)[:5]

        with transaction.atomic():
            StudentRecommendation.objects.filter(student_id=student_id).delete()
            for profession, match_pct in top5:
                level = 1 if match_pct >= 70 else (2 if match_pct >= 40 else 3)
                StudentRecommendation.objects.create(
                    student_id=student_id,
                    profession=profession,
                    match_percentage=max(0.0, min(100.0, match_pct)),
                    recommendation_level=level,
                )

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
