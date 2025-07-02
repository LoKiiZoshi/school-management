from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, CourseViewSet, ScheduleViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'', CourseViewSet, basename='course')
router.register(r'schedules', ScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]