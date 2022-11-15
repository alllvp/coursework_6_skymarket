from rest_framework import pagination, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from .models import Ad, Comment
from django_filters.rest_framework import DjangoFilterBackend
from .filters import AdFilter
from .serializers import AdSerializer, CommentSerializer, AdCreateSerializer, CommentCreateSerializer


class AdPagination(pagination.PageNumberPagination):
    page_size = 4


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    pagination_class = AdPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AdFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            self.serializer_class = AdCreateSerializer
        else:
            self.serializer_class = AdSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['retrieve', 'create', 'me']:
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list']:
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            self.serializer_class = CommentCreateSerializer
        else:
            self.serializer_class = CommentSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        ad_instance = get_object_or_404(Ad, id=self.kwargs['ad_pk'])
        return ad_instance.comment_set.all()

    def perform_create(self, serializer):
        ad_instance = get_object_or_404(Ad, id=self.kwargs['ad_pk'])
        user = self.request.user
        serializer.save(author=user, ad=ad_instance)
