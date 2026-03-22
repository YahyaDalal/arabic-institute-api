from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Certificate
from .serializers import CertificateSerializer
from config.permissions import IsAdminOrTeacher


class IssueCertificateView(generics.CreateAPIView):
    """Teacher issues a certificate — only if all criteria are met."""
    serializer_class = CertificateSerializer
    permission_classes = [IsAdminOrTeacher]

    def perform_create(self, serializer):
        certificate = serializer.save(issued_by=self.request.user)
        try:
            certificate.full_clean()
        except DjangoValidationError as e:
            certificate.delete()
            raise ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)


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