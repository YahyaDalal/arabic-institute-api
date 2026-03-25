from django.shortcuts import render

# Create your views here.
import secrets
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from rest_framework import parsers
from .serializers import RegisterSerializer, UserProfileSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        """Save the user profile."""
        return serializer.save()


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        print(f"DEBUG: Password reset requested for {email}")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'If that email exists, a reset link was sent.'})

        token = secrets.token_urlsafe(32)
        cache.set(f'pwd_reset_{token}', user.pk, timeout=3600)
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        reset_url = f"{frontend_url}/#/reset-password/confirm?token={token}"

        print(f"DEBUG: SendGrid API key present: {bool(settings.SENDGRID_API_KEY)}")
        print(f"DEBUG: Sending to: {email}")
        print(f"DEBUG: Reset URL: {reset_url}")

        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=email,
            subject='Password Reset — Arabic Institute',
            html_content=f'<p>Click to reset your password: <a href="{reset_url}">{reset_url}</a></p>'
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"DEBUG: SendGrid response status: {response.status_code}")
        except Exception as e:
            print(f"DEBUG: SendGrid error: {e}")

        return Response({'message': 'If that email exists, a reset link was sent.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        user_pk = cache.get(f'pwd_reset_{token}')
        if not user_pk:
            return Response({'error': 'Invalid or expired token.'}, status=400)
        user = User.objects.get(pk=user_pk)
        user.set_password(password)
        user.save()
        cache.delete(f'pwd_reset_{token}')
        return Response({'message': 'Password reset successful.'})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except TokenError:
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST
            )