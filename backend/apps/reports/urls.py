from django.urls import path
from .views import ClassReportView, StudentListReportView, StudentDetailReportView

urlpatterns = [
    path('reports/class/', ClassReportView.as_view(), name='class_report'),
    path('reports/students/', StudentListReportView.as_view(), name='student_list_report'),
    path('reports/students/<int:student_id>/', StudentDetailReportView.as_view(), name='student_detail_report'),
]
