from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Book(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    publication_date = models.DateField()
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=50, default='English')
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.available_quantity > self.stock_quantity:
            self.available_quantity = self.stock_quantity
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.available_quantity > 0

    class Meta:
        ordering = ['title']

class Member(models.Model):
    MEMBERSHIP_TYPES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('public', 'Public'),
        ('premium', 'Premium'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_id = models.CharField(max_length=20, unique=True)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    membership_start_date = models.DateField(auto_now_add=True)
    membership_end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    max_books_allowed = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.membership_id}"

    @property
    def is_membership_valid(self):
        return self.membership_end_date >= datetime.now().date() and self.is_active

    class Meta:
        ordering = ['membership_id']

class BookIssue(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='book_issues')
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_books')

    def __str__(self):
        return f"{self.book.title} - {self.member.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = (self.issue_date + timedelta(days=14)).date()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.due_date < datetime.now().date() and self.status == 'issued'

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (datetime.now().date() - self.due_date).days
        return 0

    class Meta:
        ordering = ['-issue_date']

class BookReservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.member.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = (self.reservation_date + timedelta(days=7)).date()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-reservation_date']
        unique_together = ['book', 'member', 'status']

class Fine(models.Model):
    FINE_TYPES = [
        ('overdue', 'Overdue Fine'),
        ('damage', 'Damage Fine'),
        ('lost', 'Lost Book Fine'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='fines')
    book_issue = models.ForeignKey(BookIssue, on_delete=models.CASCADE, related_name='fines', null=True, blank=True)
    fine_type = models.CharField(max_length=20, choices=FINE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issue_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_fines')

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.fine_type} - ${self.amount}"

    class Meta:
        ordering = ['-issue_date']

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.title} - {self.member.user.get_full_name()} - {self.rating}/5"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['book', 'member']