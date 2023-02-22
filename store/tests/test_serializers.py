from django.test import TestCase
from django.db.models import Count, Case, When, Avg
from store.models import Product
from store.serializers import ProductSerializer
from django.contrib.auth.models import User
from store.models import UserRelation


class ProductSerializerTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='Test_username 1', first_name='Ivan', last_name='Petrov')
        self.user_2 = User.objects.create(username='Test_username 2', first_name='Ivan', last_name='Ivanov')
        self.product_1 = Product.objects.create(name='Test product 1', price=25, country='Country 1', owner=self.user_1)
        self.product_2 = Product.objects.create(name='Test product 2', price=35, country='Country 2', owner=self.user_2)


    def test_ok(self):
        UserRelation.objects.create(user=self.user_1, product=self.product_1, like=True, rate=5)
        UserRelation.objects.create(user=self.user_2, product=self.product_1, like=True, rate=4)

        UserRelation.objects.create(user=self.user_1, product=self.product_2, like=False, rate=5)
        UserRelation.objects.create(user=self.user_2, product=self.product_2, like=False)

        products = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userrelation__like=True, then=1))),
            rating=Avg('userrelation__rate')
            ).order_by('id')
        data = ProductSerializer(products, many=True).data
        expected_data = [
            {
                'id': self.product_1.id,
                'name': 'Test product 1',
                'price': '25.00',
                'country': 'Country 1',
                'owner': self.product_1.owner.id,
                'annotated_likes': 2,
                'rating': '4.50',
                'owner_name': self.product_1.owner.username,
                'viewers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Ivanov',
                    },
                ]
            },
            {
                'id': self.product_2.id,
                'name': 'Test product 2',
                'price': '35.00',
                'country': 'Country 2',
                'owner': self.product_2.owner.id,
                'annotated_likes': 0,
                'rating': '5.00',
                'owner_name': self.product_2.owner.username,
                'viewers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov',
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Ivanov',
                    },

                ]                
            },
        ]
        self.assertEqual(expected_data, data)

        
