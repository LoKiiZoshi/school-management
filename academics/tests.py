from django.test import TestCase
from .models import Subject

class SubjectModelTest(TestCase):
    def test_subject_creation(self):
        subject = Subject.objects.create(name="Math", code="MATH101")
        self.assertEqual(subject.name, "Math")
