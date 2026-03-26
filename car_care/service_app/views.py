from .models import User, Vehicle, Service, Part, ServicePart
from .serializers import serialize_users, serialize_vehicles, serialize_services, serialize_parts, serialize_servicepart
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

def home(request):
    return JsonResponse({"status": "Server online"}, safe=False)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data
    try:
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data.get('email', '')
        )
        return Response({"msg": "Registration succesful!"}, status=201)
    except IntegrityError:
        return Response({"error", "Username already exists!"}, status=400)
    except Exception as e:
        return Response({"error", f"Registration failed: {e}"}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response({"user": request.user.username})


import io, csv
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_data(request):
    if 'csv_file' not in request.FILES:
        return Response({"error": "No file received!"})
    
    file_obj = request.FILES['csv_file']
    try:
        decoded_file = file_obj.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        print(reader)
        imported_count = 0
        for row in reader:
            imported_count += 1
        return Response({"msg": f"Successfully imported {imported_count} records!"})
    except UnicodeDecodeError:
        return Response({"error": "Invalid file encoding. Please select use 'UTF-8' format!"}, status=400)
    except Exception as e:
        return Response({"error": f"Error saving data: {e}"})


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

            used_parts = service_data['used_parts']
            for part in used_parts:
                part_obj = get_object_or_404(Part, id=part['part_id'])
                new_service_part = ServicePart(
                    service=new_service,
                    part=part_obj,
                    quantity_used=part['quantity']
                )
                new_service_part.full_clean()
                new_service_part.save()
            return Response({"msg", "Service and parts are added!"})
        except ValidationError as ve:
            return Response({"error": f"Validation error: {ve}"}, status=400)
        except Exception as e:
            return Response({"error", f"Error creating new service, {e}"}, status=400)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def service_details(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'DELETE':
        with transaction.atomic():
            for sp in ServicePart.objects.filter(service=service):
                sp.part.quantity += sp.quantity_used
                sp.part.save()
            service.delete()
        return Response({"msg": "Service deleted and used parts restocked!"})
    if request.method == 'PATCH':
        service_data = request.data
        try:
            with transaction.atomic():
                allowed_fields = ['title', 'description', 'date', 'odometer', 'labor_cost']
                for field in allowed_fields:
                    if field in service_data:
                        setattr(service, field, service_data[field])
                service.save()
                if 'used_parts' in service_data:
                    existing_sps = {sp.part.id: sp for sp in ServicePart.objects.filter(service=service)}
                    for item in service_data['used_parts']:
                        part_id = item.get('part_id')
                        if not part_id:
                            raise ValidationError("Error with part data")
                        incoming_qty = int(item.get('quantity', item.get('quantity_used', 0))) 
                        part_obj = get_object_or_404(Part, id=part_id)
                        if part_id in existing_sps:
                            sp = existing_sps.pop(part_id) 
                            diff = incoming_qty - sp.quantity_used
                            if diff != 0:
                                if part_obj.quantity < diff:
                                    raise ValidationError(f"Not enough {part_obj.name} in stock! (Missing: {diff - part_obj.quantity} pcs)")
                                part_obj.quantity -= diff
                                part_obj.save()
                                sp.quantity_used = incoming_qty
                                sp.save()
                        else:
                            new_sp = ServicePart(service=service, part=part_obj, quantity_used=incoming_qty)
                            new_sp.full_clean()
                            new_sp.save()      
                    for sp in existing_sps.values():
                        sp.part.quantity += sp.quantity_used
                        sp.part.save()
                        sp.delete()
            return Response({"msg": "Service details updated successfully!"})
        except ValidationError as ve:
            return Response({"error": str(ve)}, status=400)
        except Exception as e:
            return Response({"error": f"Error updating service data: {e}"}, status=400)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def parts(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'GET':
        parts = Part.objects.filter(vehicle=vehicle)
        return JsonResponse(serialize_parts(parts), safe=False)
    if request.method == 'POST':
        part_data = request.data
        try:
            new_part = Part.objects.create(
                name=part_data['name'],
                article_number=part_data['article_number'],
                quantity=part_data['quantity'],
                price=part_data['price'],
                vehicle=vehicle
            )
            return Response({"msg": "Part added!"})
        except Exception as e:
            return Response({"error": f"Error adding part, {e}"})

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def part_details(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    if request.method == 'DELETE':
        part.delete()
        return Response({"msg":"Part deleted!"})
    if request.method == 'PATCH':
        part_data = request.data
        try:
            allowed_fields = ['name', 'article_number', 'quantity', 'price']
            for field in allowed_fields:
                if field in part_data:
                    setattr(part,    field, part_data[field])
            part.save()
            return Response({"msg": "Part updated!"})
        except Exception as e:
            return Response({"error": f"Error updating part data, {e}"})