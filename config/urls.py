from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/enrolments/', include('enrolments.urls')),
    path('api/certificates/', include('certificates.urls')),
]