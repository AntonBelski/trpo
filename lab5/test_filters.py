from app.mos.models import Restaurant
from tests import BasicTestCase


class FiltersTestCase(BasicTestCase):
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
            'title': 'Testaurant_parent',
            'code': 'testaurant2',
            'short_code': 'tsa',
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

    def create_restaurant(self, restaurant_template):
        restaurant = Restaurant(**restaurant_template)
        restaurant.save()
        return restaurant

    def test_child_to_parent_filter_exists(self):
        restaurant_child = self.create_restaurant(self.restaurant_template)
        restaurant_parent = self.create_restaurant(self.restaurant_template_second)
        restaurant_child.parent = restaurant_parent
        restaurant_child.save()
        founded_child = Restaurant.objects.filter(parent__id=restaurant_parent.id)[0]
        self.assertEqual(founded_child.id, restaurant_child.id)

    def test_child_to_parent_filter_not_exists(self):
        restaurant_child = self.create_restaurant(self.restaurant_template)
        restaurant_parent = self.create_restaurant(self.restaurant_template_second)
        restaurant_child.parent = restaurant_parent
        restaurant_child.save()
        founded_childs = Restaurant.objects.filter(parent__code='not_real')
        self.assertEqual(0, len(founded_childs))

    def test_parent_to_child_filter_exists(self):
        restaurant_child = self.create_restaurant(self.restaurant_template)
        restaurant_parent = self.create_restaurant(self.restaurant_template_second)
        restaurant_child.parent = restaurant_parent
        restaurant_child.save()
        founded_restaurant = Restaurant.objects.filter(children__title=self.restaurant_template_second['title'])[0]
        self.assertEqual(founded_restaurant.id, restaurant_parent.id)

    def test_parent_to_child_filter_not_exists(self):
        restaurant_child = self.create_restaurant(self.restaurant_template)
        restaurant_parent = self.create_restaurant(self.restaurant_template_second)
        restaurant_child.parent = restaurant_parent
        restaurant_child.save()
        founded_restaurant = Restaurant.objects.filter(children__title='wrong_title')[0]
        self.assertEqual(founded_restaurant.id, restaurant_parent.id)

    def test_limit_with_start_end(self):
        restaurant_one = self.create_restaurant(self.restaurant_template)
        restaurant_two = self.create_restaurant(self.restaurant_template_second)
        found_count = len(Restaurant.objects.limit(start=0, end=2))
        self.assertEqual(2, found_count)
        found_first_restaurant = Restaurant.objects.limit(start=0, end=1)[0]
        self.assertEqual(restaurant_two.id, found_first_restaurant.id)
        found_second_restaurant = Restaurant.objects.limit(start=1, end=2)[0]
        self.assertEqual(restaurant_one.id, found_second_restaurant.id)

    def test_limit_with_start(self):
        restaurant_one = self.create_restaurant(self.restaurant_template)
        restaurant_two = self.create_restaurant(self.restaurant_template_second)
        found_count = len(Restaurant.objects.limit(start=1))
        self.assertEqual(1, found_count)

    def test_limit_with_end(self):
        restaurant_one = self.create_restaurant(self.restaurant_template)
        restaurant_two = self.create_restaurant(self.restaurant_template_second)
        found_count = len(Restaurant.objects.limit(end=1))
        self.assertEqual(1, found_count)
