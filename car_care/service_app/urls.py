from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("me/", views.get_current_user, name="current_user"),
    path("register/", views.register_user, name="register"),
    path("account/delete/", views.delete_profile, name="delete_profile"),
    path("vehicles/", views.vehicles, name="vehicles"),
    path("vehicles/<int:vehicle_id>/", views.vehicle_details, name="vehicle_details"),
    path("vehicles/<int:vehicle_id>/services/", views.services, name="services"),
    path("services/<int:service_id>/", views.service_details, name="service_details"),
    path("vehicles/<int:vehicle_id>/supplies/", views.parts, name="parts"),
    path("supplies/<int:part_id>/", views.part_details, name="part_details"),
    path("data/export/", views.export_data, name="data_export"),
    path("data/import/", views.import_data, name="data_import")
]