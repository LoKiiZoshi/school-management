from django.contrib import admin
from .models import *

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'nationality']
    list_filter = ['nationality', 'created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'publisher', 'category', 'stock_quantity', 'available_quantity']
    search_fields = ['title', 'isbn']
    list_filter = ['category', 'publisher', 'language', 'condition']
    filter_horizontal = ['authors']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'membership_id', 'membership_type', 'is_active', 'membership_end_date']
    search_fields = ['user__first_name', 'user__last_name', 'membership_id']
    list_filter = ['membership_type', 'is_active']

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'issue_date', 'due_date', 'status']
    search_fields = ['book__title', 'member__user__first_name', 'member__user__last_name']
    list_filter = ['status', 'issue_date', 'due_date']

@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'reservation_date', 'expiry_date', 'status']
    search_fields = ['book__title', 'member__user__first_name']
    list_filter = ['status', 'reservation_date']

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['member', 'fine_type', 'amount', 'status', 'issue_date']
    search_fields = ['member__user__first_name', 'member__user__last_name']
    list_filter = ['fine_type', 'status', 'issue_date']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'rating', 'created_at']
    search_fields = ['book__title', 'member__user__first_name']
    list_filter = ['rating', 'created_at']