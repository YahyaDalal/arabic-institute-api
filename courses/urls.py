from django.urls import path
from .views import CourseListCreateView, CourseDetailView, CohortListCreateView, CohortDetailView

urlpatterns = [
    path('', CourseListCreateView.as_view(), name='course-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('cohorts/', CohortListCreateView.as_view(), name='cohort-list'),
    path('cohorts/<int:pk>/', CohortDetailView.as_view(), name='cohort-detail'),
]