from django.db.models import Avg
from rest_framework import mixins, status, views, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Title


class TitleViewSet(viewsets.ModelViewSet):
    # queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    # permission_classes = (,)
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = 
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ''
        return ''
