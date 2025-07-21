from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Task, TaskSchedule, Employee, EmailLog



@shared_task
def send_task_assignment_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        subject = f"New Task Assigned: {task.title}"
        message = f"""
        Hello {task.assigned_to.user.get_full_name()},
        
        You have been assigned a new task:
        
        Title: {task.title}
        Description: {task.description}
        Priority: {task.get_priority_display()}
        Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}
        Assigned by: {task.assigned_by.user.get_full_name()}
        
        Please log in to the system to view more details.
        
        Best regards,
        Task Management System
        """
        
        email_log = EmailLog.objects.create(
            recipient=task.assigned_to,
            subject=subject,
            message=message,
            task=task
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [task.assigned_to.user.email],
            fail_silently=False,
        )
        
        email_log.sent_successfully = True
        email_log.save()
        
    except Task.DoesNotExist:
        pass
    except Exception as e:
        if 'email_log' in locals():
            email_log.error_message = str(e)
            email_log.save()

@shared_task
def send_task_reminder_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        if task.status not in ['completed', 'cancelled']:
            subject = f"Task Reminder: {task.title}"
            message = f"""
            Hello {task.assigned_to.user.get_full_name()},
            
            This is a reminder for your pending task:
            
            Title: {task.title}
            Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}
            Priority: {task.get_priority_display()}
            
            Please complete this task as soon as possible.
            
            Best regards,
            Task Management System
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [task.assigned_to.user.email],
                fail_silently=False,
            )
            
    except Task.DoesNotExist:
        pass
    

@shared_task
def create_scheduled_task(schedule_id):
    try:
        schedule = TaskSchedule.objects.get(id=schedule_id)
        if not schedule.is_active:
            return
        
        # Create task based on schedule
        due_date = timezone.now() + timedelta(days=1)  # Default 1 day from now
        
        task = Task.objects.create(
            title=schedule.task_template,
            description=schedule.description_template,
            assigned_to=schedule.assigned_to,
            assigned_by=schedule.assigned_by,
            category=schedule.category,
            priority=schedule.priority,
            due_date=due_date,
            estimated_hours=schedule.estimated_hours
        )
        
        # Send assignment email
        send_task_assignment_email.delay(task.id)
        
        # Schedule next task based on frequency
        if schedule.frequency == 'daily':
            next_run = timezone.now() + timedelta(days=1)
        elif schedule.frequency == 'weekly':
            next_run = timezone.now() + timedelta(weeks=1)
        elif schedule.frequency == 'monthly':
            next_run = timezone.now() + timedelta(days=30)
        else:
            return  # One-time task
        
        # Check if we should continue scheduling
        if schedule.end_date and next_run > schedule.end_date:
            return
        
        # Schedule next task creation
        create_scheduled_task.apply_async(args=[schedule_id], eta=next_run)
        
    except TaskSchedule.DoesNotExist:
        pass

@shared_task
def send_daily_task_summary():
    employees = Employee.objects.filter(is_active=True)
    
    for employee in employees:
        pending_tasks = Task.objects.filter(
            assigned_to=employee,
            status__in=['pending', 'in_progress']
        ).count()
        
        overdue_tasks = Task.objects.filter(
            assigned_to=employee,
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).count()
        
        if pending_tasks > 0:
            subject = f"Daily Task Summary - {pending_tasks} pending tasks"
            message = f"""
            Hello {employee.user.get_full_name()},
            
            Here's your daily task summary:
            
            Pending Tasks: {pending_tasks}
            Overdue Tasks: {overdue_tasks}
            
            Please log in to the system to manage your tasks.
            
            Best regards,
            Task Management System
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [employee.user.email],
                fail_silently=True,
            )
