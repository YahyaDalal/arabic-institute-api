from django.contrib import admin
from .models import Course, Cohort

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'status', 'pass_mark')
    list_filter = ('status',)

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'start_date', 'capacity', 'enrolment_open')