from rest_framework import serializers
from .models import *

class AuthorSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_books_count(self, obj):
        return obj.books.count()

class CategorySerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_books_count(self, obj):
        return obj.books.count()

class PublisherSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Publisher
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_books_count(self, obj):
        return obj.books.count()

class BookListSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'authors', 'category', 'publisher', 
                 'publication_date', 'price', 'available_quantity', 'cover_image']

class BookDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()

class BookCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class MemberSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    full_name = serializers.SerializerMethodField()
    active_issues_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_active_issues_count(self, obj):
        return obj.book_issues.filter(status='issued').count()

class BookIssueSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    issued_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = BookIssue
        fields = '__all__'
        read_only_fields = ['issue_date', 'issued_by']

class BookIssueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookIssue
        fields = ['book', 'member', 'due_date', 'notes']
    
    def validate(self, data):
        book = data['book']
        member = data['member']
        
        # Check if book is available
        if not book.is_available:
            raise serializers.ValidationError("Book is not available for issue")
        
        # Check member's book limit
        active_issues = member.book_issues.filter(status='issued').count()
        if active_issues >= member.max_books_allowed:
            raise serializers.ValidationError("Member has reached maximum book limit")
        
        # Check if member's membership is valid
        if not member.is_membership_valid:
            raise serializers.ValidationError("Member's membership is not valid")
        
        return data

class BookReservationSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    
    class Meta:
        model = BookReservation
        fields = '__all__'
        read_only_fields = ['reservation_date']

class FineSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    book_issue = BookIssueSerializer(read_only=True)
    processed_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Fine
        fields = '__all__'
        read_only_fields = ['issue_date', 'processed_by']

class ReviewSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
