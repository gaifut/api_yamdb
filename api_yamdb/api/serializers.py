from djoser.serializers import UserSerializer
from users.models import User
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from reviews.models import Category, Comment, Review, Genre, Title


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для получения кода, который потребуется для получения
    токена."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        validators=[UniqueValidator(queryset=User.objects.all())],
        max_length=150
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        max_length=254
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели пользователя."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z', max_length=150, required=True,
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z', max_length=150, required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=150, required=True
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
    rating = serializers.IntegerField(read_only=True)


    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field='slug'
    )
    year = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Review.objects.all(),
        #         fields=['author', 'title']
        #     )
        # ]
    
    def validate(self, data):
        title = self.context.get('title')
        author = self.context['request'].user

        existing_review = Review.objects.filter(title=title, author=author).exists()
        if existing_review:
            raise serializers.ValidationError('Можно создать только 1 отзыв на 1 произведение')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('post',)
