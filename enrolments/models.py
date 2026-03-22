from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from courses.models import Cohort

User = get_user_model()

# Enrolment model to represent a student's enrolment in a specific cohort with status, attendance, and grading information
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
    
    class Meta:
        unique_together = ('student', 'cohort')

    def clean(self):
        # Rule 1: Cohort must have enrolment open
        if not self.cohort.enrolment_open and not self.pk:
            raise ValidationError('Enrolment is closed for this cohort.')

        # Rule 2: Cohort must not be full
        if self.cohort.is_full and not self.pk:
            raise ValidationError('This cohort is full.')

        # Rule 3: Course must be published
        if self.cohort.course.status != 'published':
            raise ValidationError('Cannot enrol in an unpublished course.')

        # Rule 4: Student must have completed prerequisites
        prerequisites = self.cohort.course.prerequisites.all()
        for prereq in prerequisites:
            has_completed = Enrolment.objects.filter(
                student=self.student,
                cohort__course=prereq,
                status='completed'
            ).exists()
            if not has_completed:
                raise ValidationError(f'You must complete "{prereq.title}" before enrolling in this course.')

    def update_status(self):
        """Auto-update status based on grade and attendance."""
        if self.final_grade is None:
            return
        pass_mark = self.cohort.course.pass_mark
        if self.attendance_percentage >= 75 and self.final_grade >= pass_mark:
            self.status = self.Status.COMPLETED
        else:
            self.status = self.Status.FAILED

    @property
    def can_issue_certificate(self):
        """All five criteria must be met to issue a certificate."""
        return (
            self.status == self.Status.COMPLETED
            and self.attendance_percentage >= 75
            and self.final_grade is not None
            and self.final_grade >= self.cohort.course.pass_mark
            and self.fees_paid
            and self.teacher_approved
        )

    def __str__(self):
        return f'{self.student.email} → {self.cohort}'
