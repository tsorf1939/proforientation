from django.db import models
from apps.tests_app.models import TestResult
from apps.careers.models import Profession
from apps.users.models import Student


class ProfessionRecommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='recommendations', db_column='result_id')
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, related_name='recommendations', db_column='profession_id')
    match_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recommendation_level = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profession_recommendations'
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
        constraints = [
            models.CheckConstraint(
                check=models.Q(match_percentage__gte=0, match_percentage__lte=100),
                name='recommendation_match_range'
            ),
            models.CheckConstraint(
                check=models.Q(recommendation_level__gte=1, recommendation_level__lte=3),
                name='recommendation_level_range'
            ),
        ]
        ordering = ['-match_percentage']

    def __str__(self):
        return f'{self.profession.name} — {self.match_percentage}%'


class StudentRecommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,
                                related_name='global_recommendations', db_column='student_id')
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, db_column='profession_id')
    match_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    recommendation_level = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_recommendations'
        unique_together = ('student', 'profession')
        ordering = ['-match_percentage']

    def __str__(self):
        return f'{self.student} → {self.profession.name} {self.match_percentage}%'
