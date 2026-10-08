from django.db import models


class ClassReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey('users.Teacher', on_delete=models.CASCADE, related_name='reports')
    grade = models.IntegerField()
    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)

    class Meta:
        db_table = 'class_reports'
        verbose_name = 'Отчёт по классу'
        verbose_name_plural = 'Отчёты по классам'
        ordering = ['-generated_at']
