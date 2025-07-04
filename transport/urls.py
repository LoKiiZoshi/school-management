from django.urls import path
from . import views

urlpatterns = [
    path('api/vehicles/', views.vehicle_list, name='vehicle_list'),
    path('api/vehicles/<int:id>/', views.vehicle_detail, name='vehicle_detail'),
    path('api/bookings/', views.booking_list, name='booking_list'),
    path('api/bookings/<int:id>/', views.booking_detail, name='booking_detail'),
]