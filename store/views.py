from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import Count, Case, When, Avg
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from .models import Product, UserRelation
from .serializers import ProductSerializer, UserRelationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from store.permissions import IsAuthenticatedOwnerOrStaffReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userrelation__like=True, then=1))),
            rating=Avg('userrelation__rate')
            ).select_related('owner').prefetch_related('viewers')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticatedOwnerOrStaffReadOnly]
    filterset_fields = ['price']
    search_fields = ['name', 'country']
    ordering_fields = ['price', 'country']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserRelation.objects.all()
    serializer_class = UserRelationSerializer
    lookup_field = 'product'

    def get_object(self):
        obj, _ = UserRelation.objects.get_or_create(user=self.request.user, product_id=self.kwargs['product'])
        return obj


def auth(request):
    return render(request, 'oauth.html')

