from .models import Vehicle
from .serializers import serialize_vehicles
from django.http import JsonResponse

# Create your views here.
def vehicles_list(request):
    vehicles = Vehicle.objects.all()
    return JsonResponse(serialize_vehicles(vehicles), safe=False)