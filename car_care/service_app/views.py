from .models import User, Vehicle, Service, Part, ServicePart
from .serializers import serialize_users, serialize_vehicles, serialize_services, serialize_parts, serialize_servicepart
from django.http import JsonResponse

# Create your views here.
def home(request):
    return JsonResponse("Backend is running...", safe=False)

def users(request):
    users = User.objects.all()
    return JsonResponse(serialize_users(users), safe=False)

def vehicles(request):
    vehicles = Vehicle.objects.all()
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
