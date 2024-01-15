from django.db.models import Avg
from rest_framework import mixins, status, views, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Genre, Title


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    # permission_classes = []
    lookup_field = 'slug'
    # filter_backends = []
    search_fields = ('name',)
    # pagination_class =


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    # serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    # queryset = Title.objects
    # permission_classes = (,)
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class =
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ''
        return ''
