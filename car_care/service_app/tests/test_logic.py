from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from ..models import User, Vehicle, Part, Service, ServicePart

class ServiceLogicTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='mechanic', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            make="Suzuki",
            model="Swift",
            year=1998
        )

        self.part = Part.objects.create(
            vehicle=self.vehicle,
            name="Oil filter",
            article_number="MAN-618",
            quantity=5,
            price=6500
        )

    def test_service_reduces_inventory(self):
        url = reverse('services', kwargs={'vehicle_id': self.vehicle.id})
        service_data = {
            "title": "Oil change",
            "description": "General maintenance",
            "odometer": 275000,
            "date": "2026-03-30",
            "labor_cost": 15000,
            "used_parts": [
                {
                    "part_id": self.part.id,
                    "quantity": 2
                }]
        }
        respone = self.client.post(url, service_data, format='json')
        # Request succeed?
        self.assertEqual(respone.status_code, status.HTTP_200_OK)
        #Service created?
        self.assertEqual(Service.objects.count(), 1)
        #Supplies updated?
        self.part.refresh_from_db()
        self.assertEqual(self.part.quantity, 3)

    def test_insufficient_stock_fails(self):
        url = reverse('services', kwargs={'vehicle_id': self.vehicle.id})
        
        bad_service_data = {
            "title": "Big service",
            "description": "Too many parts",
            "odometer": 300000,
            "labor_cost": 5000,
            "used_parts": [{"part_id": self.part.id, "quantity": 10}]
        }

        response = self.client.post(url, bad_service_data, format='json')
        #Waiting for 400 error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)