from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime, timedelta
from .models import *
from .serializers import *

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'nationality']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        author = self.get_object()
        books = author.books.all()
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        category = self.get_object()
        books = category.books.all()
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)

class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        publisher = self.get_object()
        books = publisher.books.all()
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'isbn', 'authors__first_name', 'authors__last_name']
    ordering_fields = ['title', 'publication_date', 'price', 'created_at']
    filterset_fields = ['category', 'publisher', 'language', 'condition']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookCreateUpdateSerializer
        return BookDetailSerializer
    
    def get_queryset(self):
        queryset = Book.objects.all()
        available_only = self.request.query_params.get('available_only', None)
        if available_only == 'true':
            queryset = queryset.filter(available_quantity__gt=0)
        return queryset
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        book = self.get_object()
        reviews = book.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        book = self.get_object()
        member_id = request.data.get('member_id')
        
        try:
            member = Member.objects.get(id=member_id)
            reservation = BookReservation.objects.create(
                book=book,
                member=member,
                expiry_date=datetime.now().date() + timedelta(days=7)
            )
            serializer = BookReservationSerializer(reservation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'membership_id']
    ordering_fields = ['membership_id', 'created_at']
    
    @action(detail=True, methods=['get'])
    def issued_books(self, request, pk=None):
        member = self.get_object()
        issues = member.book_issues.filter(status='issued')
        serializer = BookIssueSerializer(issues, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        member = self.get_object()
        issues = member.book_issues.all()
        serializer = BookIssueSerializer(issues, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def fines(self, request, pk=None):
        member = self.get_object()
        fines = member.fines.all()
        serializer = FineSerializer(fines, many=True)
        return Response(serializer.data)

class BookIssueViewSet(viewsets.ModelViewSet):
    queryset = BookIssue.objects.all()
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['book__title', 'member__user__first_name', 'member__user__last_name']
    ordering_fields = ['issue_date', 'due_date']
    filterset_fields = ['status']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookIssueCreateSerializer
        return BookIssueSerializer
    
    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        # Decrease available quantity
        book.available_quantity -= 1
        book.save()
        
        serializer.save(issued_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        issue = self.get_object()
        if issue.status != 'issued':
            return Response({'error': 'Book is not currently issued'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        issue.return_date = datetime.now()
        issue.status = 'returned'
        
        # Calculate fine for overdue books
        if issue.is_overdue:
            fine_amount = issue.days_overdue * 1.0  # $1 per day
            Fine.objects.create(
                member=issue.member,
                book_issue=issue,
                fine_type='overdue',
                amount=fine_amount,
                description=f'Overdue fine for {issue.days_overdue} days',
                processed_by=request.user
            )
        
        # Increase available quantity
        issue.book.available_quantity += 1
        issue.book.save()
        
        issue.save()
        
        serializer = BookIssueSerializer(issue)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_issues = BookIssue.objects.filter(
            status='issued',
            due_date__lt=datetime.now().date()
        )
        serializer = BookIssueSerializer(overdue_issues, many=True)
        return Response(serializer.data)

class BookReservationViewSet(viewsets.ModelViewSet):
    queryset = BookReservation.objects.all()
    serializer_class = BookReservationSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['book__title', 'member__user__first_name', 'member__user__last_name']
    ordering_fields = ['reservation_date', 'expiry_date']
    filterset_fields = ['status']
    
    @action(detail=True, methods=['post'])
    def fulfill(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != 'active':
            return Response({'error': 'Reservation is not active'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create book issue
        issue = BookIssue.objects.create(
            book=reservation.book,
            member=reservation.member,
            issued_by=request.user
        )
        
        # Update reservation status
        reservation.status = 'fulfilled'
        reservation.save()
        
        # Decrease book availability
        reservation.book.available_quantity -= 1
        reservation.book.save()
        
        serializer = BookIssueSerializer(issue)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['member__user__first_name', 'member__user__last_name']
    ordering_fields = ['issue_date', 'amount']
    filterset_fields = ['status', 'fine_type']
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        fine = self.get_object()
        if fine.status != 'pending':
            return Response({'error': 'Fine is not pending'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        fine.status = 'paid'
        fine.payment_date = datetime.now()
        fine.save()
        
        serializer = FineSerializer(fine)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def waive(self, request, pk=None):
        fine = self.get_object()
        if fine.status != 'pending':
            return Response({'error': 'Fine is not pending'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        fine.status = 'waived'
        fine.save()
        
        serializer = FineSerializer(fine)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['book__title', 'member__user__first_name']
    ordering_fields = ['created_at', 'rating']
    filterset_fields = ['rating']
