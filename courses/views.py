from rest_framework import generics, permissions
from .models import Course, Cohort
from .serializers import CourseSerializer, CohortSerializer
from config.permissions import IsAdmin, IsAdminOrTeacher


class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Admins see all courses, others only see published
        if self.request.user.is_admin:
            return Course.objects.all()
        return Course.objects.filter(status='published')


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Course.objects.all()
        return Course.objects.filter(status='published')


class CohortListCreateView(generics.ListCreateAPIView):
    serializer_class = CohortSerializer
    queryset = Cohort.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]


class CohortDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CohortSerializer
    queryset = Cohort.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdminOrTeacher()]