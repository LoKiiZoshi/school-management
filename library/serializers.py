from rest_framework import serializers
from .models import Author, Publisher, Book, Member, BorrowRecord, Reservation


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    author_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    publisher_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Book
        fields = '__all__'
    
    def create(self, validated_data):
        author_ids = validated_data.pop('author_ids', [])
        book = super().create(validated_data)
        if author_ids:
            book.authors.set(author_ids)
        return book
    
    def update(self, instance, validated_data):
        author_ids = validated_data.pop('author_ids', None)
        book = super().update(instance, validated_data)
        if author_ids is not None:
            book.authors.set(author_ids)
        return book


class MemberSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = '__all__'
    
    def get_user_data(self, obj):
        return {
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }


class BorrowRecordSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    member_id = serializers.IntegerField(write_only=True)
    book_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    member_id = serializers.IntegerField(write_only=True)
    book_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Reservation
        fields = '__all__'