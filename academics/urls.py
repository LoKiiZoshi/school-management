from django.urls import path
from .views import SubjectListCreateView

urlpatterns = [
    path('subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
]