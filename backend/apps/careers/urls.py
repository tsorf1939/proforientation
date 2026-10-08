from django.urls import path
from .views import ProfessionListView, ProfessionDetailView

urlpatterns = [
    path('careers/', ProfessionListView.as_view(), name='career_list'),
    path('careers/<int:profession_id>/', ProfessionDetailView.as_view(), name='career_detail'),
]
