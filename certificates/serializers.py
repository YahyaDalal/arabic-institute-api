from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source='enrolment.student.email', read_only=True)
    course_title = serializers.CharField(source='enrolment.cohort.course.title', read_only=True)
    issued_by_email = serializers.EmailField(source='issued_by.email', read_only=True)

    class Meta:
        model = Certificate
        fields = ('id', 'enrolment', 'student_email', 'course_title',
                  'issued_by', 'issued_by_email', 'issued_at', 'file_url')
        read_only_fields = ('issued_by', 'issued_at')