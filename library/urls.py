from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'publishers', views.PublisherViewSet)
router.register(r'books', views.BookViewSet)
router.register(r'members', views.MemberViewSet)
router.register(r'borrow-records', views.BorrowRecordViewSet)
router.register(r'reservations', views.ReservationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
