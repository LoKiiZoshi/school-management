
# academic/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)
router.register(r'books', views.BookViewSet)
router.register(r'book-issues', views.BookIssueViewSet)
router.register(r'fee-types', views.FeeTypeViewSet)
router.register(r'fee-payments', views.FeePaymentViewSet)
router.register(r'routes', views.RouteViewSet)
router.register(r'buses', views.BusViewSet)
router.register(r'transport-registrations', views.TransportRegistrationViewSet)
router.register(r'transport-payments', views.TransportPaymentViewSet)

app_name = 'academic'