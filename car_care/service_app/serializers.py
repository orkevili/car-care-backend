from .models import Vehicle, Service, Part, ServicePart, User
from typing import Iterable, List, Dict, Any

def serialize_users(users: Iterable[User]) -> List[Dict[str, Any]]:
    data = []
    for user in users:
        data.append({
            'username': user.username,
            'email': user.email
        })

    return data

def serialize_vehicles(vehicles: Iterable[Vehicle]) -> List[Dict[str, Any]]:
    data = []
    for vehicle in vehicles:
        data.append({
            'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'license_plate': vehicle.license_plate,
            'year': vehicle.year,
            'fuel': vehicle.fuel,
            'purchase_price': vehicle.purchase_price,
            'purchase_date': vehicle.purchase_date,
            'purchase_odometer': vehicle.purchase_odometer,
            'owner': vehicle.owner.username,
        })

    return data

def serialize_services(services: Iterable[Service]) -> List[Dict[str, Any]]:
    data = []
    for service in services:
        data.append({
            'id': service.id,
            'title': service.title,
            'description': service.description,
            'odometer': service.odometer,
            'time': service.time,
            'labor_cost': service.labor_cost,
            'vehicle': service.vehicle.pk
        })

    return data

def serialize_parts(parts: Iterable[Part]) -> List[Dict[str, Any]]:
    data = []
    for part in parts:
        data.append({
            'id': part.id,
            'name': part.name,
            'article_number': part.article_number,
            'quantity': part.quantity,
            'price': part.price
        })

    return data

def serialize_servicepart(serviceparts: Iterable[ServicePart]) -> List[Dict[str, Any]]:
    data = []
    for part in serviceparts:
        data.append({
            'service_title': part.service.title,
            'part_name': part.part.name,
            'quantity_used': part.quantity_used
        })

    return data