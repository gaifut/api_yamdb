from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet, ReviewViewSet,
    SignUpView, TitleViewSet, UserViewSet, TokenView
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'genres', GenreViewSet, basename='category')
router_v1.register(r'categories', CategoryViewSet, basename='category')
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token')
]
