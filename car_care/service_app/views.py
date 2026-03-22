from .models import User, Vehicle, Service, Part, ServicePart
from .serializers import serialize_users, serialize_vehicles, serialize_services, serialize_parts, serialize_servicepart
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

def home(request):
    return JsonResponse({"status": "Server online"}, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response({"user": request.user.username})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vehicles(request):
    user = request.user
    if request.method == 'GET':
        vehicles = Vehicle.objects.filter(owner=user)
        return JsonResponse(serialize_vehicles(vehicles), safe=False)
    if request.method == 'POST':
        car_data = request.data['newCar']
        try:
            new_vehicle = Vehicle.objects.create(
                owner = user,
                make = car_data.get('make'),
                model = car_data.get('model'),
                license_plate = car_data.get('plate') or None,
                year = car_data.get('year'),
                fuel = car_data.get('fuel') or None,
                purchase_date = car_data.get('purchase_date') or None,
                purchase_price = car_data.get('purchase_price') or None,
                purchase_odometer = car_data.get('purchase_odometer') or None,
            )
            return Response({"msg": "New vehicle added to garage!"})
        except Exception as e:
            return Response({"error": f"Error during save, {e}"}, status=400)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def vehicle_details(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    if request.method == 'DELETE':
        vehicle.delete()
        return Response({"msg": "Vehicle deleted."})
    if request.method == 'PATCH':
        car_data = request.data
        try:
            allowed_fields = ['make', 'model', 'license_plate', 'year', 'fuel', 'purchase_date', 'purchase_price', 'purchase_odometer']
            for field in allowed_fields:
                if field in car_data:
                    setattr(vehicle, field, car_data[field])
            vehicle.save()
            return Response({"msg": "Vehicle updated!"})
        except Exception as e:
            return Response({"error": f"Error during update: {e}"}, status=400)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def services(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    if request.method == 'GET':
        services = Service.objects.filter(vehicle=vehicle)
        return JsonResponse(serialize_services(services), safe=False)
    if request.method == 'POST':
        service_data = request.data
        try:
            new_service = Service.objects.create(
                vehicle=vehicle,
                title = service_data['title'],
                description = service_data['description'],
                odometer = service_data['odometer'],
                date = service_data['date'],
                labor_cost = service_data['labor_cost'],
            )
            return Response({"msg", "Service added!"})
        except Exception as e:
            return Response({"error", f"Error creating new service, {e}"}, status=400)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def service_details(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'DELETE':
        service.delete()
        return Response({"msg", "Service deleted!"})
    if  request.method == 'PATCH':
        service_data = request.data
        try:
            allowed_fields = ['title', 'description', 'date', 'odometer', 'labor_cost']
            for field in allowed_fields:
                if field in allowed_fields:
                    setattr(service, field, service_data[field])
            service.save()
            return Response({"msg": "Service details updated!"})
        except Exception as e:
            return Response({"error": f"Error updating service data, {e}"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parts(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    print(vehicle)
    parts = Part.objects.filter(vehicle=vehicle)
    return JsonResponse(serialize_parts(parts), safe=False)


def serviceparts(request):
    parts = ServicePart.objects.all()
    return JsonResponse(serialize_servicepart(parts), safe=False)
