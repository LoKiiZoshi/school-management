from rest_framework import viewsets,status,filters
from rest_framework.decorators import action
from rest_framework.response import responses
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count,Avg , Sum
from datetime import date, timedelta
from .models import DepartmentSerializer, TeacherSerializer,TeacherCreateSerializer,TeacherAttendanceSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.object.all()
    serializer_class = DepartmentSerializer
    filter_backends = [ djangoFilterBakends,filter.SearchFilter]
    search_fields = ['name','code','description']
    
    
    @action(detail=True,methods=['get'])
    def teachers(self, request, pk = None):
        department = self.get_object()
        teacher = department.teacher.filters(is_active = True)
        serializer = TeacherSerializer(teachers,many = True)
        
    @action(detail =True, method = ['get'])
    def statistics(self,request,pk = Npne):
        department = self.get_object()
        teachr = department.teachers.filter(is_activate= True)
        
        stats = {
            'total_teachers':teachers.count(),
            'avg_experience':teaches.aggregate(Avg('experince_years'))['experience_years_avg'] or 0,
            
        }