from django.contrib import admin
from .models import School, Student, StudentUser, Teacher, TeacherClass

admin.site.register(School)
admin.site.register(Student)
admin.site.register(StudentUser)
admin.site.register(Teacher)
admin.site.register(TeacherClass)
