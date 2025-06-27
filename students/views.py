from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from datetime import date, timedelta
from .models import Grade, Section, Student, StudentAttendance
from .serializers import (
    GradeSerializer, SectionSerializer, StudentSerializer, 
    StudentCreateSerializer, StudentAttendanceSerializer, BulkAttendanceSerializer
)

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['level', 'name', 'created_at']
    ordering = ['level']

    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        grade = self.get_object()
        sections = grade.sections.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        grade = self.get_object()
        students = Student.objects.filter(grade=grade, is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = Grade.objects.annotate(
            sections_count=Count('sections'),
            students_count=Count('student', filter=Q(student__is_active=True))
        ).values('id', 'name', 'level', 'sections_count', 'students_count')
        return Response(stats)

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('grade').all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['grade', 'grade__level']
    search_fields = ['name', 'room_number']

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        section = self.get_object()
        students = Student.objects.filter(section=section, is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        section = self.get_object()
        students = Student.objects.filter(section=section, is_active=True)
        
        summary = []
        for student in students:
            total_days = StudentAttendance.objects.filter(student=student).count()
            present_days = StudentAttendance.objects.filter(student=student, status='P').count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            summary.append({
                'student_id': student.student_id,
                'student_name': student.user.get_full_name(),
                'total_days': total_days,
                'present_days': present_days,
                'attendance_percentage': round(attendance_percentage, 2)
            })
        
        return Response(summary)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'grade', 'section').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'section', 'gender', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'student_id', 'admission_number']
    ordering_fields = ['user__first_name', 'admission_date', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer

    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        student = self.get_object()
        attendances = StudentAttendance.objects.filter(student=student).order_by('-date')
        serializer = StudentAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        student = self.get_object()
        
        # Current month
        today = date.today()
        first_day = today.replace(day=1)
        
        total_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day
        ).count()
        
        present_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day, 
            status='P'
        ).count()
        
        late_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day, 
            status='L'
        ).count()
        
        absent_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day, 
            status='A'
        ).count()
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        return Response({
            'student_id': student.student_id,
            'student_name': student.user.get_full_name(),
            'current_month': today.strftime('%B %Y'),
            'total_days': total_days,
            'present_days': present_days,
            'late_days': late_days,
            'absent_days': absent_days,
            'attendance_percentage': round(attendance_percentage, 2)
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        student = self.get_object()
        student.is_active = False
        student.save()
        return Response({'status': 'Student deactivated successfully'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        student = self.get_object()
        student.is_active = True
        student.save()
        return Response({'status': 'Student activated successfully'})

    @action(detail=False, methods=['get'])
    def recent_admissions(self, request):
        last_30_days = date.today() - timedelta(days=30)
        recent_students = Student.objects.filter(
            admission_date__gte=last_30_days
        ).order_by('-admission_date')[:10]
        serializer = self.get_serializer(recent_students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def birthday_today(self, request):
        today = date.today()
        birthday_students = Student.objects.filter(
            date_of_birth__month=today.month,
            date_of_birth__day=today.day,
            is_active=True
        )
        serializer = self.get_serializer(birthday_students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_students = Student.objects.filter(is_active=True).count()
        total_grades = Grade.objects.count()
        total_sections = Section.objects.count()
        
        gender_stats = Student.objects.filter(is_active=True).values('gender').annotate(
            count=Count('id')
        )
        
        grade_stats = Student.objects.filter(is_active=True).values(
            'grade__name'
        ).annotate(count=Count('id'))
        
        return Response({
            'total_students': total_students,
            'total_grades': total_grades,
            'total_sections': total_sections,
            'gender_distribution': list(gender_stats),
            'grade_distribution': list(grade_stats)
        })

class StudentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendance.objects.select_related('student__user', 'recorded_by').all()
    serializer_class = StudentAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'date', 'status', 'student__grade', 'student__section']
    ordering = ['-date', 'student__roll_number']

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = BulkAttendanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            attendances = serializer.save()
            return Response({
                'message': f'Successfully recorded attendance for {len(attendances)} students',
                'count': len(attendances)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        report_date = request.query_params.get('date', date.today())
        if isinstance(report_date, str):
            from datetime import datetime
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        attendances = StudentAttendance.objects.filter(date=report_date)
        
        summary = {
            'date': report_date,
            'total_records': attendances.count(),
            'present': attendances.filter(status='P').count(),
            'absent': attendances.filter(status='A').count(),
            'late': attendances.filter(status='L').count(),
            'excused': attendances.filter(status='E').count(),
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        month = request.query_params.get('month', date.today().month)
        year = request.query_params.get('year', date.today().year)
        
        attendances = StudentAttendance.objects.filter(
            date__month=month,
            date__year=year
        )
        
        summary = {
            'month': month,
            'year': year,
            'total_records': attendances.count(),
            'present': attendances.filter(status='P').count(),
            'absent': attendances.filter(status='A').count(),
            'late': attendances.filter(status='L').count(),
            'excused': attendances.filter(status='E').count(),
        }
        
        return Response(summary)
