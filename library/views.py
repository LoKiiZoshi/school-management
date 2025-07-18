from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Author, Publisher, Book, Member, BorrowRecord, Reservation
from .serializers import (
    AuthorSerializer, PublisherSerializer, BookSerializer,
    MemberSerializer, BorrowRecordSerializer, ReservationSerializer
)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        author = self.get_object()
        books = author.books.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        publisher = self.get_object()
        books = publisher.book_set.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        available_books = Book.objects.filter(status='available', available_quantity__gt=0)
        serializer = self.get_serializer(available_books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category')
        if category:
            books = Book.objects.filter(category=category)
            serializer = self.get_serializer(books, many=True)
            return Response(serializer.data)
        return Response({'error': 'Category parameter required'}, status=400)
    
    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        book = self.get_object()
        member_id = request.data.get('member_id')
        
        if book.available_quantity <= 0:
            return Response({'error': 'Book not available'}, status=400)
        
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=404)
        
        # Create borrow record
        due_date = timezone.now() + timedelta(days=14)  # 2 weeks borrowing period
        borrow_record = BorrowRecord.objects.create(
            member=member,
            book=book,
            due_date=due_date
        )
        
        # Update book availability
        book.available_quantity -= 1
        if book.available_quantity == 0:
            book.status = 'borrowed'
        book.save()
        
        serializer = BorrowRecordSerializer(borrow_record)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        book = self.get_object()
        member_id = request.data.get('member_id')
        
        try:
            borrow_record = BorrowRecord.objects.get(
                book=book,
                member_id=member_id,
                status='active'
            )
        except BorrowRecord.DoesNotExist:
            return Response({'error': 'No active borrow record found'}, status=404)
        
        # Update borrow record
        borrow_record.return_date = timezone.now()
        borrow_record.status = 'returned'
        borrow_record.save()
        
        # Update book availability
        book.available_quantity += 1
        book.status = 'available'
        book.save()
        
        return Response({'message': 'Book returned successfully'})


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    
    @action(detail=True, methods=['get'])
    def borrow_history(self, request, pk=None):
        member = self.get_object()
        records = member.borrow_records.all()
        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def active_borrows(self, request, pk=None):
        member = self.get_object()
        active_records = member.borrow_records.filter(status='active')
        serializer = BorrowRecordSerializer(active_records, many=True)
        return Response(serializer.data)


class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_records = BorrowRecord.objects.filter(
            status='active',
            due_date__lt=timezone.now()
        )
        serializer = self.get_serializer(overdue_records, many=True)
        return Response(serializer.data)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        active_reservations = Reservation.objects.filter(
            is_active=True,
            expiry_date__gt=timezone.now()
        )
        serializer = self.get_serializer(active_reservations, many=True)
        return Response(serializer.data)