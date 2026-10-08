from django.urls import path
from .views import StudentRegisterView, TeacherRegisterView, MeView, SchoolListView, TeacherStudentView, MyStudentsView

urlpatterns = [
    path('auth/register/student/', StudentRegisterView.as_view(), name='register_student'),
    path('auth/register/teacher/', TeacherRegisterView.as_view(), name='register_teacher'),
    path('users/me/', MeView.as_view(), name='me'),
    path('schools/', SchoolListView.as_view(), name='schools'),
    path('teachers/students/', TeacherStudentView.as_view(), name='teacher_add_student'),
    path('teachers/students/<int:student_id>/', TeacherStudentView.as_view(), name='teacher_remove_student'),
    path('teachers/my-students/', MyStudentsView.as_view(), name='teacher_my_students'),
]
