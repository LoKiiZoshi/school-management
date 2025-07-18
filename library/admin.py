from django.contrib import admin
from .models import *

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'nationality']
    list_filter = ['nationality', 'created_at']

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
