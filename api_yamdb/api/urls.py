from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet, SignUpView, TitleViewSet, UserViewSet)

router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'genres', GenreViewSet, basename='category')
router_v1.register(r'categories', CategoryViewSet, basename='category')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
]
