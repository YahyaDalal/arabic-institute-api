from django.urls import path
from .views import EnrolView, MyEnrolmentsView, CohortEnrolmentsView, EnrolmentDetailView, WithdrawEnrolmentView

urlpatterns = [
    path('', EnrolView.as_view(), name='enrol'),
    path('my/', MyEnrolmentsView.as_view(), name='my-enrolments'),
    path('cohort/<int:cohort_id>/', CohortEnrolmentsView.as_view(), name='cohort-enrolments'),
    path('<int:pk>/', EnrolmentDetailView.as_view(), name='enrolment-detail'),
    path('<int:pk>/withdraw/', WithdrawEnrolmentView.as_view(), name='withdraw'),
]