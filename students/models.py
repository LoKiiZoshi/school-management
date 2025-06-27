from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator , MaxLengthValidator



# Create your models here.

class Grade(models.Model):
    name = models.CharField(max_length=50,unique=True)
    level = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['level']
        
    def __str__(self):
            return self.name
        
class Section(models.Models):
    name = models.CharField(max_length=10)
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE,related_name='section')
    capacity = models.IntegerField(default=30)
    room_number = models.CharField(max_length=20,blank=True)
    
    class Meta:
        unique_together = ['name','grade']
        
    def __str__(self):
        return f"{self.Grade.name} - {self.name}"
    
    
class Student(models.Model):
    GENDER_CHOICES = [
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),
        
    ]
    
    BLOOD_GROUP_CHOICES = [
          ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    Student_id = models.CharField(max_length=20,unique=True)
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    Section = models.ForeignKey
    

