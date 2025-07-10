from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.ManyToManyField(Author, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    publication_date = models.DateField()
    pages = models.PositiveIntegerField()
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    available_copies = models.PositiveIntegerField(default=1)
    total_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_available(self):
        return self.available_copies > 0

class Member(models.Model):
    MEMBERSHIP_TYPES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('public', 'Public'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES)
    membership_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.membership_id}"

class BookLoan(models.Model):
    LOAN_STATUS = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='borrowed')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.book.title} - {self.member.user.get_full_name()}"

class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['book', 'member']
    
    def __str__(self):
        return f"{self.book.title} - {self.rating}/5"