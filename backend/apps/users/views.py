from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import StudentRegisterSerializer, TeacherRegisterSerializer, MeSerializer, EmailTokenObtainPairSerializer
from .models import School, Student, StudentUser, TeacherStudent
from .serializers import SchoolSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class StudentRegisterView(generics.CreateAPIView):
    serializer_class = StudentRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Регистрация прошла успешно.'}, status=status.HTTP_201_CREATED)


class TeacherRegisterView(generics.CreateAPIView):
    serializer_class = TeacherRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Регистрация учителя прошла успешно.'}, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)


class SchoolListView(generics.ListAPIView):
    queryset = School.objects.all().order_by('city', 'name')
    serializer_class = SchoolSerializer
    permission_classes = [permissions.AllowAny]


class TeacherStudentView(APIView):
    """POST — добавить ученика по email; DELETE — отвязать."""
    permission_classes = [permissions.IsAuthenticated]

    def _get_teacher(self, request):
        try:
            return request.user.teacher_profile
        except Exception:
            return None

    def post(self, request):
        teacher = self._get_teacher(request)
        if not teacher:
            return Response({'detail': 'Доступ только для учителей.'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email', '').lower().strip()
        if not email:
            return Response({'detail': 'Укажите email ученика.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            return Response({'detail': 'Ученик с таким email не найден.'}, status=status.HTTP_404_NOT_FOUND)

        _, created = TeacherStudent.objects.get_or_create(teacher=teacher, student=student)
        if not created:
            return Response({'detail': 'Ученик уже добавлен.'}, status=status.HTTP_200_OK)

        return Response({
            'student_id': student.student_id,
            'full_name': f'{student.last_name} {student.first_name}',
            'email': student.email,
            'grade': student.grade,
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, student_id):
        teacher = self._get_teacher(request)
        if not teacher:
            return Response({'detail': 'Доступ только для учителей.'}, status=status.HTTP_403_FORBIDDEN)

        deleted, _ = TeacherStudent.objects.filter(teacher=teacher, student_id=student_id).delete()
        if not deleted:
            return Response({'detail': 'Ученик не найден в вашем списке.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyStudentsView(APIView):
    """GET — список учеников, привязанных к учителю."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            teacher = request.user.teacher_profile
        except Exception:
            return Response({'detail': 'Доступ только для учителей.'}, status=status.HTTP_403_FORBIDDEN)

        links = (
            TeacherStudent.objects
            .filter(teacher=teacher)
            .select_related('student')
            .order_by('student__last_name', 'student__first_name')
        )
        data = [
            {
                'student_id': lnk.student.student_id,
                'full_name': f'{lnk.student.last_name} {lnk.student.first_name}',
                'email': lnk.student.email,
                'grade': lnk.student.grade,
                'added_at': lnk.added_at,
            }
            for lnk in links
        ]
        return Response(data)
