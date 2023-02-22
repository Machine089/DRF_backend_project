from rest_framework.serializers import ModelSerializer, IntegerField, DecimalField, CharField
from .models import Product, UserRelation
from django.contrib.auth.models import User


class ProductViewersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ProductSerializer(ModelSerializer):
    annotated_likes = IntegerField(read_only=True)
    rating = DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = CharField(source='owner.username', default="", read_only=True)

    viewers = ProductViewersSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'country', 'owner', 'annotated_likes', 'rating', 'owner_name', 'viewers')


class UserRelationSerializer(ModelSerializer):
    class Meta:
        model = UserRelation
        fields = ('product', 'like', 'in_favorites', 'rate')
