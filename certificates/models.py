from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from enrolments.models import Enrolment

User = get_user_model()


class Certificate(models.Model):
    enrolment = models.OneToOneField(
        Enrolment, on_delete=models.CASCADE, related_name='certificate'
    )
    issued_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='issued_certificates'
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(blank=True)

    def clean(self):
        if not self.enrolment.can_issue_certificate:
            raise ValidationError(
                'Certificate criteria not met. Student must have completed the course, '
                'attendance ≥ 75%, grade ≥ pass mark, fees paid, and teacher approval given.'
            )

    def __str__(self):
        return f'Certificate: {self.enrolment.student.email} — {self.enrolment.cohort.course.title}'