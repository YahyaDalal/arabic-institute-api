from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Certificate
from .serializers import CertificateSerializer
from config.permissions import IsAdminOrTeacher
import cloudinary
from django.conf import settings
from .utils import upload_certificate_to_cloudinary


class IssueCertificateView(generics.CreateAPIView):
    """Teacher issues a certificate — only if all criteria are met."""
    serializer_class = CertificateSerializer
    permission_classes = [IsAdminOrTeacher]

    def perform_create(self, serializer):
        # Validate eligibility first
        enrolment = serializer.validated_data['enrolment']
        if not enrolment.can_issue_certificate:
            raise ValidationError('Certificate criteria not met.')

        # Check for duplicate
        if hasattr(enrolment, 'certificate'):
            raise ValidationError('A certificate has already been issued for this enrolment.')

        # Generate and upload PDF to Cloudinary
        student_name = enrolment.student.get_full_name() or enrolment.student.username
        course_title = enrolment.cohort.course.title
        issued_date = str(enrolment.updated_at.date())

        try:
            file_url = upload_certificate_to_cloudinary(
                student_name, course_title, issued_date
            )
        except Exception as e:
            print(f'Cloudinary upload error: {e}')
            file_url = ''

        serializer.save(issued_by=self.request.user, file_url=file_url)


class MyCertificatesView(generics.ListAPIView):
    """Student views their own certificates."""
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(enrolment__student=self.request.user)


class AllCertificatesView(generics.ListAPIView):
    """Admin/Teacher views all certificates."""
    serializer_class = CertificateSerializer
    permission_classes = [IsAdminOrTeacher]
    queryset = Certificate.objects.all()