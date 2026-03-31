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
import json

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

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile(request):
    try:
        user = request.user
        user.delete()
        return Response({"msg": "Account and all related data deleted successfully!"})
    except Exception as e:
        return Response({"error": f"Error deleting profile: {e}"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response({"user": request.user.username})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_data(request):
    user = request.user
    data = []
    try:
        vehicles = Vehicle.objects.filter(owner=user)
        for vehicle in vehicles:
            vehicle_data = {
                "make": vehicle.make,
                "model": vehicle.model,
                "license_plate": vehicle.license_plate,
                "year": vehicle.year,
                "fuel": vehicle.fuel,
                "purchase_date": vehicle.purchase_date,
                "purchase_price": vehicle.purchase_price,
                "purchase_odometer": vehicle.purchase_odometer,
                "inventory_parts": [],
                "services": []
            }

            parts = Part.objects.filter(vehicle=vehicle)
            for part in parts:
                part_data = {
                    "name": part.name,
                    "article_number": part.article_number,
                    "quantity": part.quantity,
                    "price": part.price,
                }
                vehicle_data["inventory_parts"].append(part_data)

            services = Service.objects.filter(vehicle=vehicle)
            for service in services:
                service_data = {
                    "title": service.title,
                    "description": service.description,
                    "odometer": service.odometer,
                    "date": service.date,
                    "labor_cost": service.labor_cost,
                    "used_parts": []
                }
                vehicle_data["services"].append(service_data)
                s_parts = ServicePart.objects.filter(service=service)
                for sp in s_parts:
                    sp_data = {
                        "part_name": sp.part.name,
                        "part_article_number": sp.part.article_number,
                        "quantity_used": sp.quantity_used
                    }
                    service_data["used_parts"].append(sp_data)
            data.append(vehicle_data)            
        return Response({"msg": f"Data exported! Vehicles: {len(vehicles)}, services: {len(services)}, parts: {len(parts)}",
            "backup_data": data
        }, status=200)
    except Exception as e:
        return Response({"error": f"Error during data export, {e}"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_data(request):
    if 'backup_file' not in request.FILES:
        return Response({"error": "No file received!"})
    
    file_obj = request.FILES['backup_file']
    try:
        decoded_file = file_obj.read().decode('utf-8')
        backup_data = json.loads(decoded_file)
        stats = {"vehicles_created": 0, "vehicles_updated": 0}
        with transaction.atomic():
            for v_data in backup_data:
                vehicle, v_created = Vehicle.objects.update_or_create(
                    owner = request.user,
                    make=v_data.get('make'),
                    model=v_data.get('model'),
                    license_plate=v_data.get('license_plate'),
                    defaults={
                        'year': v_data.get('year'),
                        'fuel': v_data.get('fuel'),
                        'purchase_date': v_data.get('purchase_date'),
                        'purchase_price': v_data.get('purchase_price'),
                        'purchase_odometer': v_data.get('purchase_odometer')
                    }
                )
                if v_created: stats['vehicles_created'] += 1
                else: stats['vehicles_updated'] += 1

                created_parts = {}
                for p_data in v_data.get('inventory_parts', []):
                    part, p_created = Part.objects.update_or_create(
                        vehicle=vehicle,
                        name=p_data.get('name'),
                        article_number=p_data.get('article_number'),
                        defaults={
                            'quantity': p_data.get('quantity', 0),
                            'price': p_data.get('price', 0),
                        }
                    )
                    part_key = f"{part.name}_{part.article_number}"
                    created_parts[part_key] = part
                for s_data in v_data.get('services', []):
                    service, s_created = Service.objects.update_or_create(
                        vehicle=vehicle,
                        title=s_data.get('title'),
                        description=s_data.get('description'),
                        defaults={
                            'odometer': s_data.get('odometer'),
                            'date': s_data.get('date'),
                            'labor_cost': s_data.get('labor_cost', 0),
                        }
                    )
                    for sp_data in s_data.get('used_parts', []):
                        part_key =  f"{sp_data.get('part_name')}_{sp_data.get('part_article_number')}"
                        part_obj = created_parts.get(part_key)
                        if part_obj:
                            ServicePart.objects.update_or_create(
                                service=service,
                                part=part_obj,
                                defaults={
                                'quantity_used': sp_data.get('quantity_used', 1)
                                }
                            )
        return Response({"msg": f"Done! New vehicle: {stats['vehicles_created']}, Update: {stats['vehicles_updated']}"})
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
        car_data = request.data
        try:
            with transaction.atomic():
                new_vehicle = Vehicle.objects.create(
                    owner = user,
                    make = car_data.get('make'),
                    model = car_data.get('model'),
                    license_plate = car_data.get('license_plate') or None,
                    year = car_data.get('year'),
                    fuel = car_data.get('fuel') or None,
                    purchase_date = car_data.get('purchase_date') or None,
                    purchase_price = car_data.get('purchase_price') or None,
                    purchase_odometer = car_data.get('purchase_odometer') or None,
                )
            return Response({"msg": "New vehicle added to garage!"})
        except IntegrityError:
            return Response({"error": f"Vehicle with this license plate already exists: {car_data.get('license_plate')}"}, status=400)
        except Exception as e:
            return Response({"error": f"Error during save, {e}"}, status=400)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def vehicle_details(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    if request.method == 'DELETE':
        vehicle.delete()
        return Response({"msg": "Vehicle deleted."}, status=200)
    if request.method == 'PATCH':
        car_data = request.data
        try:
            allowed_fields = ['make', 'model', 'license_plate', 'year', 'fuel', 'purchase_date', 'purchase_price', 'purchase_odometer', 'image']
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
            return Response({"msg", "Service and parts are added!"}, status=200)
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
            part, created = Part.objects.update_or_create(
                name=part_data['name'],
                article_number=part_data['article_number'],
                quantity=part_data['quantity'],
                price=part_data['price'],
                vehicle=vehicle
            )
            if not created:
                part.quantity += int(part_data['quantity'])
                part.save()
                return Response({"msg": f"Part updated! New quantity: {part.quantity}"})
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