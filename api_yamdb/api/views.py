from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView


from users.models import User
from .filters import TitleFilter
from reviews.models import Category, Comment, Genre, Review, Title
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    CategorySerializer, CommentSerializer, CustomUserSerializer, GenreSerializer, ReviewSerializer, SignUpSerializer, TitleReadSerializer,
    TitlePostSerializer
)



class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = filters.SearchFilter
    search_fields = ('name',)
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).order_by(
        'name'
    )
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitlePostSerializer

      
class SignUpView(APIView):
    """Регистрация новых пользователей через почту.
    Возможность повторного запроса кода подтверждения."""

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Запросы к пользователю.

    Регистрация администратором нового пользователя через post.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['get', 'patch'], detail=True, url_path='me')
    def my_profile(self, request):
        """Редактирование и получение личной информации.

        Права доступа: Любой авторизованный пользователь. Эндпоинт: users/me/.
        """
        ...
        
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    )
    pagination_class = PageNumberPagination

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user, title=self.get_title())

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
    
    # def update(self, request, *args, **kwargs):
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    )
    pagination_class = PageNumberPagination

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()
    
    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

