from django.db import models

class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

class Booking(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"Booking for {self.vehicle.name} on {self.date}"