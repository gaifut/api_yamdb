from djoser.serializers import UserSerializer
from users.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для получения кода, который потребуется для получения
    токена."""
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
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
