from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Enrolment
from .serializers import EnrolmentSerializer
from config.permissions import IsAdminOrTeacher


class EnrolView(generics.CreateAPIView):
    """Student enrols themselves in a cohort."""
    serializer_class = EnrolmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Build the instance without saving first
        enrolment = Enrolment(
            student=self.request.user,
            cohort=serializer.validated_data['cohort'],
            status='active'
        )
        # Run all clean() validation before touching the database
        try:
            enrolment.full_clean()
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)
        
        # Only save if validation passed
        enrolment.save()


class MyEnrolmentsView(generics.ListAPIView):
    """Student views their own enrolments."""
    serializer_class = EnrolmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrolment.objects.filter(student=self.request.user)


class CohortEnrolmentsView(generics.ListAPIView):
    """Teacher/Admin views all enrolments for a specific cohort."""
    serializer_class = EnrolmentSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        return Enrolment.objects.filter(cohort_id=self.kwargs['cohort_id'])


class EnrolmentDetailView(generics.RetrieveUpdateAPIView):
    """Teacher updates grade and attendance. System auto-updates status."""
    serializer_class = EnrolmentSerializer
    permission_classes = [IsAdminOrTeacher]
    queryset = Enrolment.objects.all()

    def perform_update(self, serializer):
        enrolment = serializer.save()
        enrolment.update_status()
        enrolment.save()


class WithdrawEnrolmentView(generics.UpdateAPIView):
    """Student withdraws from a cohort."""
    serializer_class = EnrolmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrolment.objects.filter(student=self.request.user)

    def perform_update(self, serializer):
        enrolment = serializer.instance
        if enrolment.status == 'completed':
            raise ValidationError('Cannot withdraw from a completed enrolment.')
        enrolment.status = 'withdrawn'
        enrolment.save()