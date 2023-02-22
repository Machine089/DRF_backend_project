from .models import UserRelation
from django.db.models import Count, Case, When

def set_favorites(product):
    favorites = UserRelation.objects.filter(product=product).aggregate(favorites=Count(Case(When(in_favorites=True, then=1)))).get('favorites')
    product.add_in_favorites = favorites
    product.save()

# Написать annotate для закладок
# Написать поле скидки в модели и сделать annotate для этого поля для отображения цены с учетом скидки 