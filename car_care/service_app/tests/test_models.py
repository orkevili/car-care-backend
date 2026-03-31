from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from ..models import User, Vehicle, Service, Part, ServicePart

class VehicleModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('vehicles')


    def test_vehicle_creation(self):
        payload = {
            "make": "Toyota",
            "model": "Camry",
            "year": 2020
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle = Vehicle.objects.first()
        self.assertEqual(str(vehicle), "ID: 1 | Toyota Camry (2020) - testuser")
        self.assertEqual(vehicle.year, 2020)
    

    def test_vehicle_creation_with_same_license(self):
        vehicle = Vehicle.objects.create(
            owner=self.user,
            make="Toyota",
            model="Camry",
            license_plate = "ABC-123",
            year=2020,
        )

        vehicle2 = {
            "make": "Toyota",
            "model": "Hilux",
            "license_plate": "ABC-123",
            "year": 2021,
        }
        response = self.client.post(self.url, vehicle2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vehicle.objects.count(), 1)
    

    def test_vehicle_delete(self):
        vehicle = Vehicle.objects.create(
            owner=self.user,
            make="Toyota",
            model="Camry",
            year=2020,
            license_plate="ASD-123"
        )
        url = reverse('vehicle_details', kwargs={'vehicle_id': vehicle.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vehicle.objects.count(), 0)
    

    def test_vehicle_update(self):
        vehicle = Vehicle.objects.create(
            owner=self.user,
            make="Toyota",
            model="Camry",
            year=2020,
            license_plate="ASD-123"
        )
        payload = {
            "year": 2016,
        }
        url = reverse('vehicle_details', kwargs={'vehicle_id': vehicle.id})
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.year, 2016)

class PartModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            make="Toyota",
            model="Hilux",
            year=2013,
            license_plate="ASD-123",
            purchase_odometer=228000
        )

    def test_part_create(self):
        payload = {
            "name": "Oil filter",
            "article_number": "MAN-613",
            "quantity": 2,
            "price": 6000
        }
        url = reverse('parts', kwargs={'vehicle_id': self.vehicle.id})
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Part.objects.count(), 1)
    
    def test_part_update(self):
        part = Part.objects.create(
            vehicle=self.vehicle,
            name= "Oil filter",
            article_number= "MAN-613",
            quantity= 10,
            price= 6000
        )
        payload = {
            "quantity": 2
        }
        url = reverse('part_details',kwargs={'part_id': part.id})
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        part.refresh_from_db()
        self.assertEqual(part.quantity, 2)

    def test_part_delete(self):
        part = Part.objects.create(
            vehicle=self.vehicle,
            name= "Oil filter",
            article_number= "MAN-613",
            quantity= 10,
            price= 6000
        )
        url = reverse('part_details',kwargs={'part_id': part.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Part.objects.count(), 0)

    def test_part_duplicate(self):
        payload = {
            "name": "Oil filter",
            "article_number": "MAN-613",
            "quantity": 2,
            "price": 6000
        }
        url = reverse('parts', kwargs={'vehicle_id': self.vehicle.id})
        response1 = self.client.post(url, payload, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(Part.objects.count(), 1)
        response2 = self.client.post(url, payload, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(Part.objects.count(), 1)
        self.assertEqual(Part.objects.first().quantity, 4)


class ServiceModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            make="Toyota",
            model="Hilux",
            year=2013,
            license_plate="ASD-123",
            purchase_odometer=228000
        )
        self.url = reverse('services', kwargs={'vehicle_id': self.vehicle.id})
    
    def test_service_create(self):
        payload = {
            "title": "General service",
            "description": "Oil change",
            "odometer": 230000,
            "date": "2026-03-30",
            "labor_cost": 30000,
            "used_parts": []
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Service.objects.count(), 1)
        new_service = Service.objects.first()
        self.assertEqual(new_service.title, "General service")
    
    def test_service_update(self):
        service = Service.objects.create(
            vehicle=self.vehicle,
            title="General service",
            description="Oil change",
            odometer=230000,
            date="2026-03-30",
            labor_cost=30000
        )
        payload = {
            "odometer": 100000
        }
        url = reverse('service_details', kwargs={'service_id': service.id})
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service.refresh_from_db()
        self.assertEqual(service.odometer, 100000)
    
    def test_service_add_parts(self):
        service = Service.objects.create(
            vehicle=self.vehicle,
            title="General service",
            description="Oil change",
            odometer=230000,
            date="2026-03-30",
            labor_cost=30000
        )
        payload = {
            "odometer": 100000
        }
        url = reverse('service_details', kwargs={'service_id': service.id})
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service.refresh_from_db()
        self.assertEqual(service.odometer, 100000)