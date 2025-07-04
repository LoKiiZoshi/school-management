from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Vehicle, Booking

@api_view(['GET'])
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return Response({'vehicles': [{'id': v.id, 'name': v.name} for v in vehicles]})

@api_view(['GET'])
def vehicle_detail(request, id):
    vehicle = Vehicle.objects.get(id=id)
    return Response({'id': vehicle.id, 'name': vehicle.name})

@api_view(['GET'])
def booking_list(request):
    bookings = Booking.objects.all()
    return Response({'bookings': [{'id': b.id, 'vehicle_id': b.vehicle.id} for b in bookings]})

@api_view(['GET'])
def booking_detail(request, id):
    booking = Booking.objects.get(id=id)
    return Response({'id': booking.id, 'vehicle_id': booking.vehicle.id})