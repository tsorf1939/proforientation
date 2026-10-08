from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import School, Student, StudentUser, Teacher, TeacherClass


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['school_id', 'name', 'city', 'address', 'phone']


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Принимает email + password вместо username + password."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.fields['email'] = serializers.EmailField()

    def validate(self, attrs):
        # email хранится как username в User — просто подставляем
        attrs['username'] = attrs.pop('email').lower().strip()
        return super().validate(attrs)


class StudentRegisterSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    birth_date = serializers.DateField(required=False, allow_null=True)
    email = serializers.EmailField()
    school_id = serializers.IntegerField(required=False, allow_null=True)
    grade = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=11)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.create_user(
            username=email,
            password=validated_data['password'],
            email=email,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        school = None
        if validated_data.get('school_id'):
            school = School.objects.filter(pk=validated_data['school_id']).first()

        student = Student.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            birth_date=validated_data.get('birth_date'),
            email=email,
            school=school,
            grade=validated_data.get('grade'),
        )
        StudentUser.objects.create(student=student, user=user)
        return user


class TeacherRegisterSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    school_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.create_user(
            username=email,
            password=validated_data['password'],
            email=email,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        school = None
        if validated_data.get('school_id'):
            school = School.objects.filter(pk=validated_data['school_id']).first()

        Teacher.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=email,
            school=school,
            user=user,
        )
        return user


class StudentProfileSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'birth_date', 'school', 'grade', 'email', 'registration_date']


class TeacherProfileSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ['teacher_id', 'first_name', 'last_name', 'email', 'school']


class MeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'profile']

    def get_role(self, obj):
        if hasattr(obj, 'student_profile'):
            return 'student'
        if hasattr(obj, 'teacher_profile'):
            return 'teacher'
        return 'admin'

    def get_profile(self, obj):
        if hasattr(obj, 'student_profile'):
            return StudentProfileSerializer(obj.student_profile.student).data
        if hasattr(obj, 'teacher_profile'):
            return TeacherProfileSerializer(obj.teacher_profile).data
        return None
