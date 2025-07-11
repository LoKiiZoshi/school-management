
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'publishers', views.PublisherViewSet)
router.register(r'books', views.BookViewSet)
router.register(r'members', views.MemberViewSet)
router.register(r'issues', views.BookIssueViewSet)
router.register(r'reservations', views.BookReservationViewSet)
router.register(r'fines', views.FineViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
] 