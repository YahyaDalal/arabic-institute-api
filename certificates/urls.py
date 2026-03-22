from django.urls import path
from .views import IssueCertificateView, MyCertificatesView, AllCertificatesView

urlpatterns = [
    path('', IssueCertificateView.as_view(), name='issue-certificate'),
    path('my/', MyCertificatesView.as_view(), name='my-certificates'),
    path('all/', AllCertificatesView.as_view(), name='all-certificates'),
]