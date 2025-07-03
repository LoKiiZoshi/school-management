class Route(models.Model):
    name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=200)
    end_location = models.CharField(max_length=200)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.start_location} to {self.end_location}"

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    conductor_name = models.CharField(max_length=100, blank=True)
    conductor_phone = models.CharField(max_length=15, blank=True)
    capacity = models.IntegerField()
    registration_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bus {self.bus_number} - {self.route.name}"

class TransportRegistration(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    pickup_point = models.CharField(max_length=200)
    pickup_time = models.TimeField()
    drop_time = models.TimeField()
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.user.first_name} - {self.route.name}"

class TransportPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    registration = models.ForeignKey(TransportRegistration, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    receipt_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['registration', 'month', 'year']

    def __str__(self):
        return f"{self.registration.student.user.first_name} - {self.month} {self.year}"