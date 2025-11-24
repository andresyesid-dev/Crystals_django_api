from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django_ratelimit.decorators import ratelimit
import json
import logging
from ..utils import get_client_ip, log_security_event

security_logger = logging.getLogger('security')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer to add extra claims to JWT token"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view with security logging"""
    serializer_class = CustomTokenObtainPairSerializer


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint with JWT token generation
    """
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            log_security_event(
                'LOGIN_FAILED_MISSING_CREDENTIALS',
                request,
                f"Missing credentials for login attempt"
            )
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate using Django's built-in authentication
        django_user = authenticate(request, username=username, password=password)
        
        if not django_user:
            log_security_event(
                'LOGIN_FAILED_INVALID_CREDENTIALS',
                request,
                f"Invalid credentials for user: {username}"
            )
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not django_user.is_active:
            log_security_event(
                'LOGIN_FAILED_INACTIVE_USER',
                request,
                f"Login attempt for inactive user: {username}"
            )
            return Response({
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(django_user)
        access = refresh.access_token
        
        # Add custom claims
        access['username'] = username
        access['user_id'] = django_user.id
        
        log_security_event(
            'LOGIN_SUCCESS',
            request,
            f"Successful login for user: {username}",
            user=username
        )
        
        return Response({
            'message': '✅ Inicio de sesión exitoso',
            'access': str(access),
            'refresh': str(refresh),
            'user': {
                'id': django_user.id,
                'username': django_user.username,
                'email': django_user.email,
                'is_staff': django_user.is_staff,
                'is_superuser': django_user.is_superuser
            }
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        log_security_event(
            'LOGIN_FAILED_INVALID_JSON',
            request,
            "Invalid JSON in login request"
        )
        return Response({
            'error': 'Invalid JSON format'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        security_logger.error(f"Login error: {str(e)}", extra={
            'extra_ip': get_client_ip(request),
            'extra_user': 'Unknown'
        })
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint - blacklist refresh token
    """
    try:
        refresh_token = request.data.get('refresh_token') or request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Blacklist the refresh token
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as blacklist_error:
            # Log the specific blacklist error but continue
            security_logger.warning(f"Blacklist error: {str(blacklist_error)}", extra={
                'extra_ip': get_client_ip(request),
                'extra_user': getattr(request.user, 'username', 'Unknown')
            })
            
        log_security_event(
            'LOGOUT_SUCCESS',
            request,
            f"User logged out: {getattr(request.user, 'username', 'Unknown')}",
            user=getattr(request.user, 'username', 'Unknown')
        )
        
        return Response({
            'message': '✅ Cierre de sesión exitoso'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        security_logger.error(f"Logout error: {str(e)}", extra={
            'extra_ip': get_client_ip(request),
            'extra_user': getattr(request.user, 'username', 'Unknown')
        })
        return Response({
            'error': f'Logout failed: {str(e)}',
            'detail': 'Please check server logs for more information'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def refresh_token(request):
    """
    Refresh token endpoint
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        new_access = token.access_token
        
        return Response({
            'message': '✅ Token renovado exitosamente',
            'access_token': str(new_access),
            'token_type': 'Bearer',
            'expires_in': 3600
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        log_security_event(
            'TOKEN_REFRESH_FAILED',
            request,
            f"Token refresh failed: {str(e)}"
        )
        return Response({
            'message': '❌ Error al renovar token',
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify token endpoint - returns user info if token is valid
    """
    try:
        # Get user from custom User model
        custom_user = User.objects.filter(username=request.user.username).first()
        
        if not custom_user:
            return Response({
                'message': '❌ Usuario no encontrado',
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': '✅ Token verificado exitosamente',
            'valid': True,
            'user': {
                'id': custom_user.id,
                'username': custom_user.username
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': '❌ Error al verificar token',
            'error': 'Token verification failed'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user profile
    """
    try:
        custom_user = User.objects.filter(username=request.user.username).first()
        
        if not custom_user:
            return Response({
                'message': '❌ Usuario no encontrado',
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': '✅ Perfil de usuario obtenido exitosamente',
            'user': {
                'id': custom_user.id,
                'username': custom_user.username,
                'last_login': request.user.last_login,
                'date_joined': request.user.date_joined
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'message': '❌ Error al obtener perfil de usuario',
            'error': 'Failed to get user profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)