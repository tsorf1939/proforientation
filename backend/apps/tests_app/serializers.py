from rest_framework import serializers
from .models import Test, TestQuestion, AnswerOption, TestResult, StudentAnswer


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['option_id', 'option_text']


class TestQuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = TestQuestion
        fields = ['question_id', 'question_text', 'question_type', 'question_order', 'options']


class TestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['test_id', 'name', 'description', 'questions_count', 'duration_minutes', 'test_type', 'task_number']


class TestDetailSerializer(serializers.ModelSerializer):
    questions = TestQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ['test_id', 'name', 'description', 'questions_count', 'duration_minutes', 'test_type', 'task_number', 'questions']


class TestResultSerializer(serializers.ModelSerializer):
    test = TestListSerializer(read_only=True)

    class Meta:
        model = TestResult
        fields = ['result_id', 'test', 'start_date', 'completion_date', 'status']


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    option_id = serializers.IntegerField(required=False, allow_null=True)
    answer_text = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        try:
            question = TestQuestion.objects.select_related('test').get(pk=data['question_id'])
        except TestQuestion.DoesNotExist:
            raise serializers.ValidationError({'question_id': 'Вопрос не найден.'})

        data['question'] = question

        if question.question_type == 'text_input':
            data['option'] = None
            return data

        option_id = data.get('option_id')
        if not option_id:
            raise serializers.ValidationError({'option_id': 'Для данного вопроса необходимо выбрать вариант ответа.'})

        try:
            option = AnswerOption.objects.get(pk=option_id, question=question)
        except AnswerOption.DoesNotExist:
            raise serializers.ValidationError({'option_id': 'Вариант ответа не найден или не принадлежит вопросу.'})

        data['option'] = option
        return data
