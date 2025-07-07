from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class FeeCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    
    class Meta:
        verbose_name_plural = "Fee Categories"
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    class FeeStructure(models.Model):
        FREQUENCY_CHOICES = [
            ('monthly','Monthly'),
            ('quarterly','Quarterly'),
            ('semester','Semester'),
            ('annual','Annual'),
        ]
        
        category = models.ForeignKey(FeeCategory,on_delete = models.CASCADE)
        name = models.CharField(max_length=100),
        amount = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))])
        frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES,default='monthly')
        due_date = models.DateField()
        late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default= 0)
        is_mandatory = models.BooleanField(default=True)
        is_active = models.BooleanField(default=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now_add=True)
        
        class Meta:
            ordering = ['category','name']
            
        def __str__(self):
            return f"{self.student_id}-{self.first_name}{self.last_name}"
        
        @property
        def full_name(self):
            return f"{self.first_name}{self.last_name}"
        
        class FeePayment(models.Model):
            PAYMENT_STATUS_CHOICES = [4
                                      ]