from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from store.models import Product, UserRelation
from store.other_code import set_favorites


class ModelsTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='Test_username 1')
        self.user_2 = User.objects.create(username='Test_username 2')

        self.product_1 = Product.objects.create(
            name='Test product 1', 
            price=25, 
            country='Country 1', 
            owner=self.user_1
        )

        self.product_2 = Product.objects.create(
            name='Test product 2', 
            price=35, 
            country='Country 2', 
            owner=self.user_2
        )

        UserRelation.objects.create(
            user=self.user_1,
            product=self.product_1,
            like=True,
            rate=5,
            in_favorites=True
        )

        UserRelation.objects.create(
            user=self.user_2,
            product=self.product_1,
            like=True,
            rate=5,
            in_favorites=True
        )

    def test_in_favorites(self):
        set_favorites(self.product_1)
        self.product_1.refresh_from_db()
        self.assertEqual(2, self.product_1.add_in_favorites)