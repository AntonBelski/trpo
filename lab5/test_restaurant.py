from uuid import UUID

from app.core.database.exception import ValidationError
from app.mos.models import Restaurant
from tests import BasicTestCase, TestUtils


class RestaurantTestCase(BasicTestCase, TestUtils):
    def setUp(self):
        super().setUp()

        self.restaurant_template = {
            'title': 'Testaurant',
            'code': 'testaurant',
            'short_code': 'tsr',
            'description': 'test',
            'about': 'test'
        }

        self.restaurant_template_second = {
            'title': 'Testaurant',
            'code': 'testaurant',
            'short_code': 'tsr',
            'description': 'test',
            'about': 'test'
        }

        self.restaurant_template_update = {
            'title': 'Cooler Testaurant',
            'code': 'cool_testaurant',
            'short_code': 'cts',
            'description': 'cooler test',
            'about': 'test but cool'
        }

    def test_create_restaurant(self):
        restaurant = self.create_restaurant(self.restaurant_template)
        self.assertIsNotNone(restaurant.id)

    def test_read_restaurant(self):
        restaurant = self.create_restaurant(self.restaurant_template)
        search_id = UUID(restaurant.id)
        restaurant_found = Restaurant.objects.get(id=search_id)
        self.assertIsNotNone(restaurant_found)

    def test_update_restaurant(self):
        restaurant = self.create_restaurant(self.restaurant_template)
        search_id = UUID(restaurant.id)
        self.restaurant_template_update.update({'id': search_id})

        restaurant_second = Restaurant.objects.get(id=search_id)
        restaurant_second.save(**self.restaurant_template_update)

        restaurant_third = Restaurant.objects.get(id=search_id)

        self.assertEqual(
            (self.restaurant_template_update['title'], self.restaurant_template_update['code']),
            (restaurant_third.title, restaurant_third.code)
        )

    def test_delete_restaurant(self):
        restaurant = self.create_restaurant(self.restaurant_template)
        delete_id = UUID(restaurant.id)
        restaurant_for_delete = Restaurant.objects.get(id=delete_id)
        self.assertIsNotNone(restaurant_for_delete)
        deleted = restaurant_for_delete.delete()
        self.assertTrue(deleted)

    def test_create_will_raise_exception_short_name_max_length_constraint(self):
        self.restaurant_template['short_code'] = 'more_than_3_symbols'
        with self.assertRaises(ValidationError):
            self.create_restaurant(self.restaurant_template)

    def test_update_will_raise_exception_short_name_max_length_constraint(self):
        restaurant = self.create_restaurant(self.restaurant_template)
        search_id = UUID(restaurant.id)
        self.restaurant_template_update.update({'id': search_id, 'short_code': 'more_than_3_symbols'})
        restaurant_second = Restaurant.objects.get(id=search_id)
        with self.assertRaises(ValidationError):
            restaurant_second.save(**self.restaurant_template_update)
