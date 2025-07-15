from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()
router.register(r'exam-types', views.ExamTypeViewSet, basename='examtype')
router.register(r'exams', views.ExamViewSet, basename='exam')
router.register(r'results', views.ResultViewSet, basename='result')
router.register(r'assignments', views.AssignmentViewSet, basename='assignment')
router.register(r'submissions', views.SubmissionViewSet, basename='submission')

app_name = 'exams'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Exam URLs
    path('exams/', views.ExamListView.as_view(), name='exam_list'),
    path('exams/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    
    # Result URLs
    path('results/', views.ResultListView.as_view(), name='result_list'),
    
    # Assignment URLs
    path('assignments/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    
    # API endpoints with custom actions
    path('api/exams/<int:pk>/publish/', views.ExamViewSet.as_view({'post': 'publish'}), name='exam_publish'),
    path('api/exams/<int:pk>/statistics/', views.ExamViewSet.as_view({'get': 'statistics'}), name='exam_statistics'),
    path('api/results/my-results/', views.ResultViewSet.as_view({'get': 'my_results'}), name='my_results'),
    path('api/assignments/<int:pk>/publish/', views.AssignmentViewSet.as_view({'post': 'publish'}), name='assignment_publish'),
]