from .models import User, Vehicle, Service, Part, ServicePart
from .serializers import serialize_users, serialize_vehicles, serialize_services, serialize_parts, serialize_servicepart
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
def home(request):
    return JsonResponse({"status": "Server online"}, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response({"user": request.user.username})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vehicles(request):
    user = request.user
    if request.method == 'GET':
        vehicles = Vehicle.objects.filter(owner=user)
        return JsonResponse(serialize_vehicles(vehicles), safe=False)
    if request.method == 'POST':
        car_data = request.data.get('newCar', {})
        try:
            new_vehicle = Vehicle.objects.create(
                owner = user,
                make = car_data.get('brand'),
                license_plate = car_data.get('plate'),
                year = car_data.get('year'),
                fuel = car_data.get('fuel'),
                puchase_date = car_data.get('puchase_date'),
                purchase_price = car_data.get('purchase_price'),
                puchase_odometer = car_data.get('puchase_odometer'),
            )
            return Response({"msg": "New vehicle added to garage!"})
        except Exception as e:
            return Response({"error": f"Error during save, {e}"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def services(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    print(vehicle)
    services = Service.objects.filter(vehicle=vehicle)
    print(services)
    return JsonResponse(serialize_services(services), safe=False)

def parts(request):
    parts = Part.objects.all()
    return JsonResponse(serialize_parts(parts), safe=False)

def serviceparts(request):
    parts = ServicePart.objects.all()
    return JsonResponse(serialize_servicepart(parts), safe=False)
