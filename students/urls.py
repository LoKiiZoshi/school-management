from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet, SectionViewSet, StudentViewSet, StudentAttendanceViewSet

router = DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'', StudentViewSet, basename='student')
router.register(r'attendance', StudentAttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]