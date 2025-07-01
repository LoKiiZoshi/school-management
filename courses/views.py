from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Subject, Course, Schedule
from .serializers import SubjectSerializer, CourseSerializer, ScheduleSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['is_mandatory', 'credit_hours']
    ordering_fields = ['name', 'code', 'credit_hours', 'created_at']

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        subject = self.get_object()
        courses = subject.courses.filter(is_active=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        subject = self.get_object()
        from teachers.serializers import TeacherSerializer
        teachers = subject.teachers.filter(is_active=True)
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = Subject.objects.aggregate(
            total_subjects=Count('id'),
            mandatory_subjects=Count('id', filter=models.Q(is_mandatory=True)),
            total_credit_hours=models.Sum('credit_hours')
        )
        return Response(stats)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('grade').prefetch_related('subjects').all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['grade', 'semester', 'is_active']
    ordering_fields = ['name', 'grade__level', 'created_at']

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        course = self.get_object()
        schedules = course.schedules.filter(is_active=True).order_by('day_of_week', 'start_time')
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        course = self.get_object()
        subjects = course.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        from students.models import Grade
        stats = {
            'total_courses': Course.objects.filter(is_active=True).count(),
            'courses_by_grade': list(Course.objects.filter(is_active=True).values('grade__name').annotate(count=Count('id'))),
            'courses_by_semester': list(Course.objects.filter(is_active=True).values('semester').annotate(count=Count('id'))),
            'total_subjects': Subject.objects.count()
        }
        return Response(stats)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related('course', 'subject', 'teacher__user', 'section__grade').all()
    serializer_class = ScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'subject', 'teacher', 'section', 'day_of_week', 'is_active']
    search_fields = ['subject__name', 'teacher__user__first_name', 'room_number']
    ordering = ['day_of_week', 'start_time']

    @action(detail=False, methods=['get'])
    def teacher_schedule(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if not teacher_id:
            return Response({'error': 'teacher_id parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            teacher_id=teacher_id, 
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def section_schedule(self, request):
        section_id = request.query_params.get('section_id')
        if not section_id:
            return Response({'error': 'section_id parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            section_id=section_id, 
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def room_schedule(self, request):
        room_number = request.query_params.get('room_number')
        if not room_number:
            return Response({'error': 'room_number parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            room_number=room_number, 
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def daily_schedule(self, request):
        day = request.query_params.get('day')
        if not day:
            return Response({'error': 'day parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            day_of_week=day.upper(), 
            is_active=True
        ).order_by('start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
