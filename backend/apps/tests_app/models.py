from django.db import models
from apps.users.models import Student


class Test(models.Model):
    TEST_TYPE_CHOICES = [
        ('career', 'Профориентация'),
        ('klimov', 'Тип по Климову'),
        ('temperament', 'Темперамент'),
        ('scored', 'Балльное задание'),
        ('reflection', 'Рефлексивное задание'),
    ]

    test_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    questions_count = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(null=True, blank=True)
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES, default='career')
    task_number = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'tests'
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.name


class TestQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('single_choice', 'Одиночный выбор'),
        ('text_input', 'Текстовый ввод'),
    ]

    question_id = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions', db_column='test_id')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='single_choice')
    question_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'test_questions'
        ordering = ['question_order']
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f'[{self.test.name}] {self.question_text[:60]}'


class AnswerOption(models.Model):
    option_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name='options', db_column='question_id')
    option_text = models.CharField(max_length=300)
    # Веса по 6 категориям (Казакова)
    weight_people = models.IntegerField(default=0)
    weight_intellectual = models.IntegerField(default=0)
    weight_practical = models.IntegerField(default=0)
    weight_aesthetic = models.IntegerField(default=0)
    weight_physical = models.IntegerField(default=0)
    weight_administrative = models.IntegerField(default=0)

    class Meta:
        db_table = 'answer_options'
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'


class TestResult(models.Model):
    STATUS_IN_PROGRESS = 'в_процессе'
    STATUS_COMPLETED = 'завершено'
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, 'В процессе'),
        (STATUS_COMPLETED, 'Завершено'),
    ]

    result_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='test_results', db_column='student_id')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results', db_column='test_id')
    start_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)

    class Meta:
        db_table = 'test_results'
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'
        unique_together = ('student', 'test')

    def __str__(self):
        return f'{self.student} — {self.test.name} [{self.status}]'


class StudentAnswer(models.Model):
    answer_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='answers', db_column='student_id')
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name='student_answers', db_column='question_id')
    answer_text = models.TextField(blank=True, null=True)  # оставлено для совместимости
    option = models.ForeignKey(AnswerOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_answers', db_column='option_id')

    class Meta:
        db_table = 'student_answers'
        verbose_name = 'Ответ учащегося'
        verbose_name_plural = 'Ответы учащихся'
        unique_together = ('student', 'question')

    def __str__(self):
        return f'{self.student} → вопрос #{self.question_id}'
