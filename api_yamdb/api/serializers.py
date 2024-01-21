from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Review, Genre, Title
from users.models import User
from api_yamdb.settings import (
    MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME, MAX_LENGTH_CONFIRMATION_CODE
)
from .validators import validate_username


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для запроса на получение кода, который потребуется
    для получения токена."""
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME, required=True,
        validators=[UnicodeUsernameValidator(), validate_username]
    )
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL, required=True
    )


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для запроса модели пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для запроса на получение токена."""
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME, required=True,
        validators=[UnicodeUsernameValidator(), validate_username]
    )
    confirmation_code = serializers.CharField(
        max_length=MAX_LENGTH_CONFIRMATION_CODE, required=True
    )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer(many=False)
    rating = serializers.SerializerMethodField(
        read_only=True, default=None
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        total_scores = []
        for review in Review.objects.filter(title=obj.id):
            total_scores.append(review.score)
        if not total_scores:
            return None
        return round(sum(total_scores) / len(total_scores))


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, value):
        return TitleReadSerializer(value).data


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        if request.method == 'POST':
            if Review.objects.filter(title=title_id, author=author).exists():
                raise serializers.ValidationError(
                    'Можно создать только 1 отзыв на 1 произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
