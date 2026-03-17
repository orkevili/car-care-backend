from django.contrib import admin
from .models import Vehicle, Part, Service, ServicePart

# Register your models here.
admin.site.register(Vehicle)
admin.site.register(Part)
admin.site.register(Service)
admin.site.register(ServicePart)