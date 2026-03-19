from .models import User, Vehicle, Service, Part, ServicePart
from .serializers import serialize_users, serialize_vehicles, serialize_services, serialize_parts, serialize_servicepart
from django.http import JsonResponse
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
    vehicles = Vehicle.objects.filter(owner=user)
    return JsonResponse(serialize_vehicles(vehicles), safe=False)

def services(request):
    services = Service.objects.all()
    return JsonResponse(serialize_services(services), safe=False)

def parts(request):
    parts = Part.objects.all()
    return JsonResponse(serialize_parts(parts), safe=False)

def serviceparts(request):
    parts = ServicePart.objects.all()
    return JsonResponse(serialize_servicepart(parts), safe=False)
