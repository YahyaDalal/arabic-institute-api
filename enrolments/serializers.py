from rest_framework import serializers
from .models import Enrolment


class EnrolmentSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source='student.email', read_only=True)
    cohort_info = serializers.StringRelatedField(source='cohort', read_only=True)
    course_title = serializers.CharField(source='cohort.course.title', read_only=True)
    can_issue_certificate = serializers.BooleanField(read_only=True)

    class Meta:
        model = Enrolment
        fields = ('id', 'student', 'student_email', 'cohort', 'cohort_info', 'course_title',
                  'status', 'attendance_percentage', 'final_grade',
                  'fees_paid', 'teacher_approved', 'can_issue_certificate',
                  'enrolled_at', 'updated_at')
        read_only_fields = ('student', 'status', 'enrolled_at', 'updated_at')