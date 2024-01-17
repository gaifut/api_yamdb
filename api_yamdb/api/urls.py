from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet, SignUpView

router_v1 = routers.SimpleRouter()
# Регистрация новых пользователей пост-запросом от администрата:
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    # Самостоятельная регистрация новых пользователей через почту:
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
]
