from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from courses.models import Cohort

User = get_user_model()


class Enrolment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolments')
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='enrolments')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fees_paid = models.BooleanField(default=False)
    teacher_approved = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
