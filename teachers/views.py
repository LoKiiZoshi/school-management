from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum
from datetime import date, timedelta
from .models import Department, Teacher, TeacherAttendance
from .serializers import DepartmentSerializer, TeacherSerializer, TeacherCreateSerializer, TeacherAttendanceSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'code', 'description']

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        department = self.get_object()
        teachers = department.teachers.filter(is_active=True)
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        department = self.get_object()
        teachers = department.teachers.filter(is_active=True)
        
        stats = {
            'total_teachers': teachers.count(),
            'avg_experience': teachers.aggregate(Avg('experience_years'))['experience_years__avg'] or 0,
            'employment_types': teachers.values('employment_type').annotate(count=Count('id')),
            'gender_distribution': teachers.values('gender').annotate(count=Count('id'))
        }
        return Response(stats)

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user', 'department').prefetch_related('subjects').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'employment_type', 'gender', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'teacher_id', 'employee_id']
    ordering_fields = ['user__first_name', 'joining_date', 'experience_years']

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        return TeacherSerializer

    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        teacher = self.get_object()
        attendances = TeacherAttendance.objects.filter(teacher=teacher).order_by('-date')
        serializer = TeacherAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        teacher = self.get_object()
        
        today = date.today()
        first_day = today.replace(day=1)
        
        total_days = TeacherAttendance.objects.filter(
            teacher=teacher, 
            date__gte=first_day
        ).count()
        
        present_days = TeacherAttendance.objects.filter(
            teacher=teacher, 
            date__gte=first_day, 
            status='P'
        ).count()
        
        return Response({
            'teacher_id': teacher.teacher_id,
            'teacher_name': teacher.user.get_full_name(),
            'total_days': total_days,
            'present_days': present_days,
            'attendance_percentage': (present_days / total_days * 100) if total_days > 0 else 0
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        teachers = Teacher.objects.filter(is_active=True)
        
        stats = {
            'total_teachers': teachers.count(),
            'departments': Department.objects.count(),
            'avg_experience': teachers.aggregate(Avg('experience_years'))['experience_years__avg'] or 0,
            'avg_salary': teachers.aggregate(Avg('salary'))['salary__avg'] or 0,
            'employment_distribution': list(teachers.values('employment_type').annotate(count=Count('id'))),
            'department_distribution': list(teachers.values('department__name').annotate(count=Count('id')))
        }
        return Response(stats)

class TeacherAttendanceViewSet(viewsets.ModelViewSet):
    queryset = TeacherAttendance.objects.select_related('teacher__user', 'teacher__department').all()
    serializer_class = TeacherAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['teacher', 'date', 'status', 'teacher__department']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        report_date = request.query_params.get('date', date.today())
        if isinstance(report_date, str):
            from datetime import datetime
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        attendances = TeacherAttendance.objects.filter(date=report_date)
        
        summary = {
            'date': report_date,
            'total_records': attendances.count(),
            'present': attendances.filter(status='P').count(),
            'absent': attendances.filter(status='A').count(),
            'late': attendances.filter(status='L').count(),
            'half_leave': attendances.filter(status='HL').count(),
            'full_leave': attendances.filter(status='FL').count(),
            'avg_working_hours': attendances.aggregate(Avg('working_hours'))['working_hours__avg'] or 0
        }
        
        return Response(summary)
