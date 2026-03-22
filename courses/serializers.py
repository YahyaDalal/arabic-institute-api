from rest_framework import serializers
from .models import Course, Cohort


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'level', 'status', 'prerequisites', 'pass_mark', 'created_at')
        read_only_fields = ('created_at',)


class CohortSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    teacher_email = serializers.EmailField(source='teacher.email', read_only=True)
    current_enrolment_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cohort
        fields = ('id', 'course', 'course_title', 'teacher', 'teacher_email',
                  'start_date', 'end_date', 'capacity', 'enrolment_open',
                  'current_enrolment_count', 'is_full')