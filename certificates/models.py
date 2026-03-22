from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    pass_mark = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} ({self.status})'

# Cohort model to represent specific offerings of a course with a teacher and schedule

class Cohort(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cohorts')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cohorts')
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField(default=30)
    enrolment_open = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.course.title} — {self.start_date}'

    @property
    def current_enrolment_count(self):
        return self.enrolments.filter(status__in=['pending', 'active']).count()

    @property
    def is_full(self):
        return self.current_enrolment_count >= self.capacity