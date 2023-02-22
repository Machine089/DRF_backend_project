from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Product, UserRelation


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass


@admin.register(UserRelation)
class UserRelationAdmin(ModelAdmin):
    pass

