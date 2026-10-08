from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TestResult

_RECOMMENDATION_TASK_NUMBERS = {12, 13, 14, 15}


@receiver(post_save, sender=TestResult)
def on_test_completed(sender, instance, **kwargs):
    if instance.status != TestResult.STATUS_COMPLETED:
        return

    from apps.recommendations.tasks import generate_recommendations
    generate_recommendations.delay(instance.result_id)

    if instance.test.task_number in _RECOMMENDATION_TASK_NUMBERS:
        completed = set(
            TestResult.objects
            .filter(student=instance.student, status=TestResult.STATUS_COMPLETED,
                    test__task_number__in=_RECOMMENDATION_TASK_NUMBERS)
            .values_list('test__task_number', flat=True)
        )
        if completed >= _RECOMMENDATION_TASK_NUMBERS:
            from apps.recommendations.tasks import generate_student_recommendations
            generate_student_recommendations.delay(instance.student_id)
