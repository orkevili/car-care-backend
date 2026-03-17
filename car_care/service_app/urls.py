from django.urls import path
from . import views

urlpatterns = [
    path("/users", views.users, name="users"),
    path("/vehicles", views.vehicles, name="vehicles"),
    path("/services", views.services, name="services"),
    path("/parts", views.parts, name="parts"),
    path("/serviceparts", views.serviceparts, name="serviceparts"),
]