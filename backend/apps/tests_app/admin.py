from django.contrib import admin
from .models import Test, TestQuestion, AnswerOption, TestResult, StudentAnswer


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4


class TestQuestionInline(admin.StackedInline):
    model = TestQuestion
    extra = 1


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'name', 'questions_count', 'duration_minutes']
    inlines = [TestQuestionInline]


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'test', 'question_text']
    inlines = [AnswerOptionInline]


admin.site.register(TestResult)
admin.site.register(StudentAnswer)
