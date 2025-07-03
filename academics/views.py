from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from datetime import date, timedelta
from .models import ExamType, Exam, Result, Assignment, Submission
from .serializers import (ExamTypeSerializer, ExamSerializer, ResultSerializer, 
                         AssignmentSerializer, SubmissionSerializer)

class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = 