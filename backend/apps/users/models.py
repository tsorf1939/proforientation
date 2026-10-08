from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    school_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'schools'
        verbose_name = 'Школа'
        verbose_name_plural = 'Школы'

    def __str__(self):
        return f'{self.name} ({self.city})'


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, db_column='school_id')
    grade = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Учащийся'
        verbose_name_plural = 'Учащиеся'
        constraints = [
            models.CheckConstraint(check=models.Q(grade__gte=1, grade__lte=11), name='student_grade_range')
        ]

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class StudentUser(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='user_link', db_column='student_id')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', db_column='django_user_id')

    class Meta:
        db_table = 'student_users'
        verbose_name = 'Пользователь-студент'
        verbose_name_plural = 'Пользователи-студенты'


class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, db_column='school_id')
    email = models.EmailField(max_length=100, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', db_column='django_user_id')

    class Meta:
        db_table = 'teachers'
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class TeacherClass(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='classes', db_column='teacher_id')
    grade = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.CASCADE, db_column='school_id')

    class Meta:
        db_table = 'teacher_classes'
        verbose_name = 'Класс учителя'
        verbose_name_plural = 'Классы учителей'
        constraints = [
            models.CheckConstraint(check=models.Q(grade__gte=1, grade__lte=11), name='teacher_class_grade_range')
        ]
        unique_together = ('teacher', 'grade', 'school')


class TeacherStudent(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='linked_students', db_column='teacher_id')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='linked_teachers', db_column='student_id')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teacher_students'
        unique_together = ('teacher', 'student')
        verbose_name = 'Ученик учителя'
        verbose_name_plural = 'Ученики учителей'
