from django.urls import path
from . import views

urlpatterns = [
    path("", views.vehicles_list, name="vehicles")
]