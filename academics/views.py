from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ExamType, Exam, Result, Assignment, Submission
from .serializers import (
    ExamTypeSerializer, ExamSerializer, ResultSerializer, 
    AssignmentSerializer, SubmissionSerializer
)
from .forms import ExamForm, ResultForm, AssignmentForm, SubmissionForm

# REST API ViewSets
class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ExamType.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Exam.objects.select_related('exam_type', 'grade', 'subject')
        
        # Filter by grade
        grade_id = self.request.query_params.get('grade', None)
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject', None)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        # Filter by exam type
        exam_type_id = self.request.query_params.get('exam_type', None)
        if exam_type_id:
            queryset = queryset.filter(exam_type_id=exam_type_id)
        
        # Filter by published status
        is_published = self.request.query_params.get('is_published', None)
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == 'true')
        
        return queryset.order_by('-exam_date')

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        exam = self.get_object()
        exam.is_published = True
        exam.save()
        return Response({'status': 'exam published'})

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        exam = self.get_object()
        results = exam.results.all()
        
        stats = {
            'total_students': results.count(),
            'passed_students': results.filter(is_passed=True).count(),
            'failed_students': results.filter(is_passed=False).count(),
            'average_marks': results.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0,
            'average_percentage': results.aggregate(Avg('percentage'))['percentage__avg'] or 0,
            'grade_distribution': {}
        }
        
        # Calculate grade distribution
        for grade_choice in Result.GRADE_CHOICES:
            grade_code = grade_choice[0]
            count = results.filter(grade=grade_code).count()
            stats['grade_distribution'][grade_code] = count
        
        return Response(stats)

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Result.objects.select_related('student', 'exam')
        
        # Filter by student
        student_id = self.request.query_params.get('student', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Filter by exam
        exam_id = self.request.query_params.get('exam', None)
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        
        # Filter by grade
        grade = self.request.query_params.get('grade', None)
        if grade:
            queryset = queryset.filter(grade=grade)
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def my_results(self, request):
        if hasattr(request.user, 'student_profile'):
            results = Result.objects.filter(
                student=request.user.student_profile
            ).select_related('exam', 'exam__subject', 'exam__exam_type')
            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)
        return Response({'error': 'Student profile not found'}, status=400)

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Assignment.objects.select_related('course', 'subject', 'teacher')
        
        # Filter by course
        course_id = self.request.query_params.get('course', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject', None)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by teacher (if user is teacher)
        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        assignment = self.get_object()
        assignment.status = 'PUBLISHED'
        assignment.save()
        return Response({'status': 'assignment published'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        assignment = self.get_object()
        assignment.status = 'CLOSED'
        assignment.save()
        return Response({'status': 'assignment closed'})

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        assignment = self.get_object()
        submissions = assignment.submissions.select_related('student')
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Submission.objects.select_related('assignment', 'student', 'graded_by')
        
        # Filter by assignment
        assignment_id = self.request.query_params.get('assignment', None)
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        
        # Filter by student
        student_id = self.request.query_params.get('student', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # If user is student, only show their submissions
        if hasattr(self.request.user, 'student_profile'):
            queryset = queryset.filter(student=self.request.user.student_profile)
        
        return queryset.order_by('-submitted_at')

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        submission = self.get_object()
        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')
        
        if marks is not None:
            submission.marks_obtained = marks
            submission.feedback = feedback
            submission.graded_by = request.user.teacher_profile
            submission.graded_at = timezone.now()
            submission.save()
            
            serializer = self.get_serializer(submission)
            return Response(serializer.data)
        
        return Response({'error': 'Marks are required'}, status=400)

# Traditional Django Views
class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 10

    def get_queryset(self):
        queryset = Exam.objects.select_related('exam_type', 'grade', 'subject')
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(subject__name__icontains=search_query) |
                Q(grade__name__icontains=search_query)
            )
        return queryset.order_by('-exam_date')

class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'exams/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.get_object()
        context['results'] = exam.results.select_related('student').order_by('-marks_obtained')
        return context

class ResultListView(LoginRequiredMixin, ListView):
    model = Result
    template_name = 'exams/result_list.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        queryset = Result.objects.select_related('student', 'exam')
        
        # If user is student, only show their results
        if hasattr(self.request.user, 'student_profile'):
            queryset = queryset.filter(student=self.request.user.student_profile)
        
        return queryset.order_by('-created_at')

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Assignment.objects.select_related('course', 'subject', 'teacher')
        
        # If user is teacher, only show their assignments
        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        
        return queryset.order_by('-created_at')

class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.get_object()
        
        # Check if current user has submitted
        if hasattr(self.request.user, 'student_profile'):
            try:
                submission = Submission.objects.get(
                    assignment=assignment,
                    student=self.request.user.student_profile
                )
                context['user_submission'] = submission
            except Submission.DoesNotExist:
                context['user_submission'] = None
        
        return context

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, "Only students can submit assignments.")
        return redirect('assignment_detail', pk=assignment_id)
    
    # Check if already submitted
    existing_submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user.student_profile
    ).first()
    
    if existing_submission:
        messages.warning(request, "You have already submitted this assignment.")
        return redirect('assignment_detail', pk=assignment_id)
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user.student_profile
            submission.save()
            messages.success(request, "Assignment submitted successfully!")
            return redirect('assignment_detail', pk=assignment_id)
    else:
        form = SubmissionForm()
    
    return render(request, 'assignments/submit_assignment.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
def dashboard(request):
    context = {}
    
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        context.update({
            'recent_results': Result.objects.filter(student=student).order_by('-created_at')[:5],
            'pending_assignments': Assignment.objects.filter(
                status='PUBLISHED',
                due_date__gt=timezone.now()
            ).exclude(
                submissions__student=student
            )[:5],
            'user_type': 'student'
        })
    
    elif hasattr(request.user, 'teacher_profile'):
        teacher = request.user.teacher_profile
        context.update({
            'recent_assignments': Assignment.objects.filter(teacher=teacher).order_by('-created_at')[:5],
            'pending_submissions': Submission.objects.filter(
                assignment__teacher=teacher,
                marks_obtained__isnull=True
            ).count(),
            'user_type': 'teacher'
        })
    
    return render(request, 'dashboard.html', context)