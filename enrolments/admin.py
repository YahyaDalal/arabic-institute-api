from django.contrib import admin
from .models import Enrolment

@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'cohort', 'status', 'attendance_percentage', 'final_grade', 'fees_paid', 'teacher_approved')
    list_filter = ('status',)