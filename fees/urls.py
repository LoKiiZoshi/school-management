from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Create router and register viewsets
router = DefaultRouter()
router.register(r'schools', SchoolViewSet)
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'students', StudentViewSet)
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'student-fees', StudentFeeViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'discounts', DiscountViewSet)
router.register(r'student-discounts', StudentDiscountViewSet)

# URL patterns
urlpatterns = [
    path('api/v1/', include(router.urls)),
    
    # Authentication URLs
    path('api/v1/auth/', include('rest_framework.urls')),
    
    # Custom API endpoints
    path('api/v1/schools/<uuid:pk>/dashboard/', SchoolViewSet.as_view({'get': 'dashboard'}), name='school-dashboard'),
    path('api/v1/academic-years/<uuid:pk>/set-current/', AcademicYearViewSet.as_view({'post': 'set_current'}), name='set-current-year'),
    path('api/v1/classes/<uuid:pk>/students/', ClassViewSet.as_view({'get': 'students'}), name='class-students'),
    path('api/v1/classes/<uuid:pk>/fee-summary/', ClassViewSet.as_view({'get': 'fee_summary'}), name='class-fee-summary'),
    path('api/v1/students/<uuid:pk>/fees/', StudentViewSet.as_view({'get': 'fees'}), name='student-fees'),
    path('api/v1/students/<uuid:pk>/payments/', StudentViewSet.as_view({'get': 'payments'}), name='student-payments'),
    path('api/v1/students/<uuid:pk>/fee-summary/', StudentViewSet.as_view({'get': 'fee_summary'}), name='student-fee-summary'),
    path('api/v1/fee-structures/bulk-create/', FeeStructureViewSet.as_view({'post': 'bulk_create'}), name='bulk-create-fees'),
    path('api/v1/student-fees/pending/', StudentFeeViewSet.as_view({'get': 'pending_fees'}), name='pending-fees'),
    path('api/v1/student-fees/overdue/', StudentFeeViewSet.as_view({'get': 'overdue_fees'}), name='overdue-fees'),
    path('api/v1/student-fees/<uuid:pk>/apply-discount/', StudentFeeViewSet.as_view({'post': 'apply_discount'}), name='apply-discount'),
    path('api/v1/payments/collect/', PaymentViewSet.as_view({'post': 'collect_payment'}), name='collect-payment'),
    path('api/v1/payments/<uuid:pk>/receipt/', PaymentViewSet.as_view({'get': 'receipt'}), name='payment-receipt'),
    path('api/v1/payments/daily-collection/', PaymentViewSet.as_view({'get': 'daily_collection'}), name='daily-collection'),
    path('api/v1/discounts/<uuid:pk>/apply-to-student/', DiscountViewSet.as_view({'post': 'apply_to_student'}), name='apply-discount-to-student'),
]
