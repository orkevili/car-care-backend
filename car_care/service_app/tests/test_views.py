from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ..models import User, Vehicle

class VehicleAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password123')
        self.client.force_authenticate(user=self.user)

    def test_get_vehicles_list(self):
        url = reverse('vehicles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)