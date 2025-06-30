from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, TeacherViewSet, TeacherAttendanceViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'', TeacherViewSet, basename='teacher')
router.register(r'attendance', TeacherAttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]