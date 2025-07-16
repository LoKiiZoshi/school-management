from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.forms import ModelForm, DateInput, TimeInput, DateTimeInput
from .models import ExamType, Exam, Result, Assignment, Submission

class ExamTypeForm(ModelForm):
    class Meta:
        model = ExamType
        fields = ['name', 'description', 'weight_percentage', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter exam type name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description (optional)'
            }),
            'weight_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_weight_percentage(self):
        weight = self.cleaned_data.get('weight_percentage')
        if weight and (weight < 0 or weight > 100):
            raise ValidationError("Weight percentage must be between 0 and 100.")
        return weight

class ExamForm(ModelForm):
    class Meta:
        model = Exam
        fields = [
            'name', 'exam_type', 'grade', 'subject', 'exam_date', 
            'start_time', 'duration_minutes', 'total_marks', 
            'passing_marks', 'instructions', 'is_published'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter exam name'
            }),
            'exam_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'exam_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Duration in minutes'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Total marks'
            }),
            'passing_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Passing marks'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Exam instructions (optional)'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active exam types
        self.fields['exam_type'].queryset = ExamType.objects.filter(is_active=True)
    
    def clean_exam_date(self):
        exam_date = self.cleaned_data.get('exam_date')
        if exam_date and exam_date < timezone.now().date():
            raise ValidationError("Exam date cannot be in the past.")
        return exam_date
    
    def clean_passing_marks(self):
        passing_marks = self.cleaned_data.get('passing_marks')
        total_marks = self.cleaned_data.get('total_marks')
        
        if passing_marks and total_marks:
            if passing_marks > total_marks:
                raise ValidationError("Passing marks cannot be greater than total marks.")
            if passing_marks < 1:
                raise ValidationError("Passing marks must be at least 1.")
        
        return passing_marks
    
    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration and duration < 1:
            raise ValidationError("Duration must be at least 1 minute.")
        return duration

class ResultForm(ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'exam', 'marks_obtained', 'remarks']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'exam': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Marks obtained'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional remarks (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only published exams
        self.fields['exam'].queryset = Exam.objects.filter(is_published=True)
    
    def clean_marks_obtained(self):
        marks = self.cleaned_data.get('marks_obtained')
        exam = self.cleaned_data.get('exam')
        
        if marks is not None and marks < 0:
            raise ValidationError("Marks cannot be negative.")
        
        if marks and exam:
            if marks > exam.total_marks:
                raise ValidationError(f"Marks cannot exceed total marks ({exam.total_marks}).")
        
        return marks
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        exam = cleaned_data.get('exam')
        
        if student and exam:
            # Check if result already exists
            if Result.objects.filter(student=student, exam=exam).exists():
                raise ValidationError("Result for this student and exam already exists.")
        
        return cleaned_data

class AssignmentForm(ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'course', 'subject', 'teacher',
            'due_date', 'total_marks', 'status', 'attachment', 'instructions'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter assignment title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter assignment description'
            }),
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'teacher': forms.Select(attrs={
                'class': 'form-control'
            }),
            'due_date': DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Total marks'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Assignment instructions (optional)'
            })
        }
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            raise ValidationError("Due date cannot be in the past.")
        return due_date
    
    def clean_total_marks(self):
        total_marks = self.cleaned_data.get('total_marks')
        if total_marks and total_marks < 1:
            raise ValidationError("Total marks must be at least 1.")
        return total_marks

class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ['submission_text', 'attachment']
        widgets = {
            'submission_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter your submission text here...'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.zip'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        submission_text = cleaned_data.get('submission_text')
        attachment = cleaned_data.get('attachment')
        
        if not submission_text and not attachment:
            raise ValidationError("Please provide either submission text or upload an attachment.")
        
        return cleaned_data

class GradeSubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ['marks_obtained', 'feedback']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Marks obtained'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide feedback to the student...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop('assignment', None)
        super().__init__(*args, **kwargs)
        
        if self.assignment:
            self.fields['marks_obtained'].widget.attrs['max'] = str(self.assignment.total_marks)
    
    def clean_marks_obtained(self):
        marks = self.cleaned_data.get('marks_obtained')
        
        if marks is not None and marks < 0:
            raise ValidationError("Marks cannot be negative.")
        
        if marks and self.assignment:
            if marks > self.assignment.total_marks:
                raise ValidationError(f"Marks cannot exceed total marks ({self.assignment.total_marks}).")
        
        return marks

# Additional specialized forms
class ExamSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search exams...'
        })
    )
    exam_type = forms.ModelChoiceField(
        queryset=ExamType.objects.filter(is_active=True),
        required=False,
        empty_label="All Exam Types",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    grade = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Grades",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    subject = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Subjects",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You'll need to import these models
        # from students.models import Grade
        # from courses.models import Subject
        # self.fields['grade'].queryset = Grade.objects.all()
        # self.fields['subject'].queryset = Subject.objects.all()

class ResultFilterForm(forms.Form):
    GRADE_CHOICES = [('', 'All Grades')] + Result.GRADE_CHOICES
    
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    passed = forms.ChoiceField(
        choices=[('', 'All'), ('True', 'Passed'), ('False', 'Failed')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    exam_type = forms.ModelChoiceField(
        queryset=ExamType.objects.filter(is_active=True),
        required=False,
        empty_label="All Exam Types",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

class AssignmentFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Status')] + Assignment.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    subject = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Subjects",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    course = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label="All Courses",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

class BulkResultForm(forms.Form):
    """Form for bulk result entry"""
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Upload CSV file with columns: student_id, marks_obtained, remarks'
    )
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.filter(is_published=True),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if file:
            if not file.name.endswith('.csv'):
                raise ValidationError("File must be in CSV format.")
            
            # Additional validation for file size
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("File size cannot exceed 5MB.")
        
        return file

