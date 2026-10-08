from django.urls import path
from .views import TestListView, TestDetailView, SubmitAnswerView, MyTestResultsView, TestResultDetailView, ResultScoresView, ResultAnswersView, DeleteResultView

urlpatterns = [
    path('tests/', TestListView.as_view(), name='test_list'),
    path('tests/<int:test_id>/', TestDetailView.as_view(), name='test_detail'),
    path('tests/answer/', SubmitAnswerView.as_view(), name='submit_answer'),
    path('results/', MyTestResultsView.as_view(), name='my_results'),
    path('results/<int:result_id>/', TestResultDetailView.as_view(), name='result_detail'),
    path('results/<int:result_id>/delete/', DeleteResultView.as_view(), name='delete_result'),
    path('results/<int:result_id>/scores/', ResultScoresView.as_view(), name='result_scores'),
    path('results/<int:result_id>/answers/', ResultAnswersView.as_view(), name='result_answers'),
]
