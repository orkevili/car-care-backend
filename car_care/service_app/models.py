from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Vehicle(models.Model):
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    license_plate = models.CharField(max_length=24, unique=True, null=True, blank=True)
    year = models.IntegerField()
    fuel = models.CharField(max_length=24, null=True, blank=True)
    purchase_date = models.DateField(default=timezone.now, null=True, blank=True)
    purchase_price = models.IntegerField(null=True, blank=True)
    purchase_odometer = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')

    def __str__(self):
        return f"ID: {self.pk} | {self.make} {self.model} ({self.year}) - {self.owner.username}"

class Service(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    odometer = models.IntegerField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    labor_cost = models.IntegerField(default=0)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return f"ID: {self.pk} | {self.title}({self.vehicle.model}) - {self.labor_cost} | {self.date}"

class Part(models.Model):
    name = models.CharField(max_length=255)
    article_number = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='parts')

    def __str__(self):
        return f"ID: {self.pk} | {self.name} - {self.quantity}pc, {self.price}/quantity"

class ServicePart(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_parts')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='used_in_services')
    quantity_used = models.IntegerField(default=1)

    def __str__(self):
        return f"ID: {self.pk} | {self.service.title} - {self.part.name} ({self.quantity_used} pc)"
    
    def clean(self):
        if not self.pk and self.quantity_used > self.part.quantity:
                raise ValidationError({'quantity_used': f"Not enough parts in stock! ({self.part.quantity} pc)"})
        if self.service.vehicle != self.part.vehicle:
            raise ValidationError({'part': f"This part belongs to a different vehicle!"})

    def save(self, *args, **kwargs):
        if not self.pk:
            self.part.quantity -= self.quantity_used
            self.part.save()
        super().save(*args, **kwargs)

