from django.urls import path
from .views import MyRecommendationsView, ResultRecommendationsView, StudentRecommendationsView

urlpatterns = [
    path('recommendations/', MyRecommendationsView.as_view(), name='my_recommendations'),
    path('recommendations/global/', StudentRecommendationsView.as_view(), name='student_recommendations'),
    path('results/<int:result_id>/recommendations/', ResultRecommendationsView.as_view(), name='result_recommendations'),
]
