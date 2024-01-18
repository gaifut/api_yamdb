from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api_yamdb import settings
from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsAuthorAdminSuperuserOrReadOnlyPermission,
    IsAdminPermission
)
from .serializers import (
    CategorySerializer, CommentSerializer, CustomUserSerializer,
    GenreSerializer, ReviewSerializer, SignUpSerializer,
    TitleReadSerializer, TitlePostSerializer, TokenSerializer
)


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = filters.SearchFilter,
    search_fields = ('name',)
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitlePostSerializer


class SignUpView(APIView):
    """Регистрация новых пользователей через почту.
    Возможность повторного запроса кода подтверждения."""

    def get_or_create_user(self, **validated_data):
        """Получение или создание объекта пользователя."""
        user, is_create = User.objects.get_or_create(
            **validated_data
        )
        return user, is_create

    def send_confirmation_code(self, user):
        """Отправка письма с кодом подтверждения."""
        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Проверочный код',
            message=f'Проверочный код: {confirmation_code}',
            from_email=settings.EMAIL,
            recipient_list=(user.email,),
            fail_silently=False
        )

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            user, _ = self.get_or_create_user(
                **serializer.validated_data
            )
            self.send_confirmation_code(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        user, _ = self.get_or_create_user(
            **serializer.validated_data
        )
        self.send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Запросы к пользователю.

    Регистрация администратором нового пользователя через post.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminPermission,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(
        methods=['get', 'patch'], detail=False, url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def my_profile(self, request):
        """Редактирование и получение личной информации.

        Права доступа: Любой авторизованный пользователь. Эндпоинт: users/me/.
        """
        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """Получение токена."""

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorAdminSuperuserOrReadOnlyPermission,
    )
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def perform_create(self, serializer):
        title = self.get_title()
        author = self.request.user

        try:
            serializer.save(author=author, title=title)
        except IntegrityError:
            existing_review = Review.objects.get(author=author, title=title)
            serializer.instance = existing_review
            serializer.save()

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthorAdminSuperuserOrReadOnlyPermission,
    )
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()
