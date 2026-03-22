from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("me/", views.get_current_user, name="current_user"),
    path("vehicles/", views.vehicles, name="vehicles"),
    path("vehicles/<int:vehicle_id>/", views.vehicle_details, name="vehicle_details"),
    path("vehicles/<int:vehicle_id>/services/", views.services, name="services"),
    path("services/<int:service_id>/", views.service_details, name="service_details"),
    path("parts/", views.parts, name="parts"),
    path("serviceparts/", views.serviceparts, name="serviceparts"),
]