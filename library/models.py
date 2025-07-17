from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class TimestampMixin(models.Model):
    """Abstract base class for timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class BookStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    BORROWED = 'borrowed', 'Borrowed'
    RESERVED = 'reserved', 'Reserved'
    MAINTENANCE = 'maintenance', 'Under Maintenance'
    LOST = 'lost', 'Lost'


class BookCategory(models.TextChoices):
    FICTION = 'fiction', 'Fiction'
    NON_FICTION = 'non_fiction', 'Non-Fiction'
    SCIENCE = 'science', 'Science'
    TECHNOLOGY = 'technology', 'Technology'
    HISTORY = 'history', 'History'
    BIOGRAPHY = 'biography', 'Biography'
    CHILDREN = 'children', 'Children'
    REFERENCE = 'reference', 'Reference'


class MembershipType(models.TextChoices):
    STUDENT = 'student', 'Student'
    FACULTY = 'faculty', 'Faculty'
    STAFF = 'staff', 'Staff'
    PUBLIC = 'public', 'Public'


class BorrowStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    RETURNED = 'returned', 'Returned'
    OVERDUE = 'overdue', 'Overdue'
    LOST = 'lost', 'Lost'


class Author(TimestampMixin):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Publisher(TimestampMixin):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Book(TimestampMixin):
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True)
    publication_date = models.DateField()
    category = models.CharField(max_length=20, choices=BookCategory.choices)
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=50, default='English')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=BookStatus.choices, default=BookStatus.AVAILABLE)
    quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class Member(TimestampMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_id = models.CharField(max_length=20, unique=True)
    membership_type = models.CharField(max_length=20, choices=MembershipType.choices)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.membership_id})"
    
    class Meta:
        ordering = ['membership_id']


class BorrowRecord(TimestampMixin):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=BorrowStatus.choices, default=BorrowStatus.ACTIVE)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.book.title}"
    
    class Meta:
        ordering = ['-borrow_date']


class Reservation(TimestampMixin):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.book.title}"
    
    class Meta:
        ordering = ['-reservation_date']