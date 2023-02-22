from rest_framework.test import APITestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.db.models import Count, Case, When, Avg
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product, UserRelation
from store.serializers import ProductSerializer

import json


class ProductApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="Test_username")
        self.product_1 = Product.objects.create(name='Test product 1', price=25, country='Country 1', owner=self.user)
        self.product_2 = Product.objects.create(name='Test product 2', price=35, country='Country 3', owner=self.user)
        self.product_3 = Product.objects.create(name='Test product 3 Country 1', price=35, country='Country 2', owner=self.user)

    def test_queries(self):
        url = reverse('product-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual(2, len(queries))

    def test_get(self):
        url = reverse('product-list')
        response = self.client.get(url)
        products = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userrelation__like=True, then=1))),
            rating=Avg('userrelation__rate')).order_by('id')
        serializer_data = ProductSerializer(products, many=True).data 
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], None)

    def test_get_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'price': 35})
        products = Product.objects.filter(id__in=[self.product_2.id, self.product_3.id]).annotate(
            annotated_likes=Count(Case(When(userrelation__like=True, then=1))),
            rating=Avg('userrelation__rate'))
        serializer_data = ProductSerializer(products, many=True).data 
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'search': 'Country 1'})
        products = Product.objects.filter(id__in=[self.product_1.id, self.product_3.id]).annotate(
            annotated_likes=Count(Case(When(userrelation__like=True, then=1))),
            rating=Avg('userrelation__rate'))
        serializer_data = ProductSerializer(products, many=True).data 
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'ordering': 'price'})
        products = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userrelation__like=True, then=1))),
            rating=Avg('userrelation__rate')).order_by('id')
        serializer_data = ProductSerializer(products, many=True).data 
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-list')
        
        data = {
            "name": 'Cheese',
            "price": 52,
            "country": 'Italy'
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Product.objects.all().count())
        self.assertEqual(self.user, Product.objects.last().owner)

    def test_read(self):
        url = reverse('product-list')
        response = self.client.get(url)
        products = Product.objects.all().annotate(
            annotated_likes=Count(Case(When(userrelation__like=True, then=1))),
            rating=Avg('userrelation__rate')).order_by('id')
        serializer_data = ProductSerializer(products, many=True).data 
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update(self):
        url = reverse('product-detail', args=(self.product_1.id,))

        data = {
            "name": self.product_1.name,
            "price": 40,
            "country": self.product_1.country
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        # self.product_1 = Product.objects.get(id=self.product_1.id)
        self.product_1.refresh_from_db()

        self.assertEqual(40, self.product_1.price)

    def test_delete(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-detail', args=(self.product_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Product.objects.all().count())

    def test_update_not_owner(self):
        self.user_2 = User.objects.create(username="Test username 2")
        url = reverse('product-detail', args=(self.product_1.id,))
        
        data = {
            "name": self.product_1.name,
            "price": 40,
            "country": self.product_1.country
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user_2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.product_1.refresh_from_db()
        self.assertEqual(25, self.product_1.price)

    def test_update_not_owner_but_staff(self):
        self.user_2 = User.objects.create(username="Test username 2", is_staff=True)
        url = reverse('product-detail', args=(self.product_1.id,))

        data = {
            "name": self.product_1.name,
            "price": 40,
            "country": self.product_1.country
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user_2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.product_1.refresh_from_db()
        self.assertEqual(40, self.product_1.price)


class ProductRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="Test_username")
        self.user_2 = User.objects.create(username="Test_username2")
        self.product_1 = Product.objects.create(name='Test product 1', price=25, country='Country 1', owner=self.user)
        self.product_2 = Product.objects.create(name='Test product 2', price=35, country='Country 3', owner=self.user_2)

    def test_like(self):
        url = reverse('userrelation-detail', args=(self.product_1.id,))

        data = {
            "like": True,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)        
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)        
        relation = UserRelation.objects.get(user=self.user, product=self.product_1)
        self.assertTrue(relation.like)
        
    def test_in_favorites(self): 
        url = reverse('userrelation-detail', args=(self.product_1.id,)) 

        data = {
            "in_favorites": True,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)        
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code) 
        relation = UserRelation.objects.get(user=self.user, product=self.product_1)
        self.assertTrue(relation.in_favorites)

    def test_rate(self):
        url = reverse('userrelation-detail', args=(self.product_1.id,)) 

        data = {
            "rate": 3,
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)        
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code) 
        relation = UserRelation.objects.get(user=self.user, product=self.product_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userrelation-detail', args=(self.product_1.id,)) 

        data = {
            "rate": 6,
        }
        
        json_data = json.dumps(data)
        self.client.force_login(self.user)        
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code) 
