import os
import random
import unittest
from datetime import datetime

from app import app
from app.core.database import GraphDb, element, properties
from app.mos.constants import RESTAURANT_RESOURCE_TYPE_MENU, RESTAURANT_RESOURCE_TYPE_FILE
from app.mos.models import *
from app.mos.models import MenuItemResourceTypeRelation, ResourceType, Revision
from app.mos.models.file import File, ImageFile, FileRelation, MediaResourceRelation, CertificateFile, \
    ApplicationFile, RawFile, FileResourceTypeRelation
from app.mos.models.file import MediaResource
from app.mos.models.menu import MenuItemMediaResourceRelation


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('settings.config')
        self.app = app.test_client()
        self.db = GraphDb(os.environ.get('DB_NEPTUNE_HOST'), os.environ.get('DB_NEPTUNE_PORT'))

    def tearDown(self):
        self.db.get_traversal().V().drop().iterate()


class TestUtils(object):
    def create_restaurant(self, restaurant_template):
        restaurant = Restaurant(**restaurant_template)
        restaurant.save()
        return restaurant

    def create_mod_group(self, template, save=True):
        obj = ModifierGroup(**template)
        if save:
            obj.save()
        return obj

    def create_modifier(self, template, save=True):
        obj = Modifier(**template)
        if save:
            obj.save()
        return obj

    def create_menu_item(self, template, save=True):
        obj = MenuItem(**template)
        if save:
            obj.save()
        return obj

    def create_menu_category(self, template, save=True):
        obj = MenuCategory(**template)
        if save:
            obj.save()
        return obj

    def create_slide(self, template, save=True):
        obj = Slide(**template)
        if save:
            obj.save()
        return obj

    def create_slide_action(self, template, save=True):
        obj = SlideAction(**template)
        if save:
            obj.save()
        return obj

    def create_slide_group(self, template, save=True):
        obj = SlideGroup(**template)
        if save:
            obj.save()
        return obj

    def create_file(self, save=True):
        file = File()
        file.hash = f'{random.getrandbits(128):32x}'
        file.file_size = random.randint(100, 1000)

        if save:
            file.save()

        return file

    def create_image(self, save=True):
        file = self.create_file(save=True)

        mr = MediaResource()
        mr.name = "Main Image"
        mr.description = "Main Description"

        mr.save()

        img_file = ImageFile()
        img_file.uri = "example.com/img.jpg"
        img_file.file = FileRelation(source=img_file, target=file)
        img_file.media_resource = MediaResourceRelation(source=mr, target=img_file)

        if save:
            img_file.save()

        return img_file, file, mr

    def create_certificate_file(self, template, save=True):
        file = self.create_file(save=True)

        obj = CertificateFile(**template)

        obj.file = FileRelation(source=obj, target=file)

        if save:
            obj.save()
        return obj

    def create_application_file(self, template, save=True):
        obj = ApplicationFile(**template)
        if save:
            obj.save()
        return obj

    def create_raw_file(self, template, save=True):
        obj = RawFile(**template)
        if save:
            obj.save()
        return obj

    def create_revision_with_nested_objects(self):
        self.g = self.db.get_traversal()

        self.restaurant_template = {
            'title': 'Testaurant',
            'code': 'testaurant',
            'short_code': 'tsr',
            'description': 'test',
            'about': 'test'
        }

        self.img_template = {
            'title': 'Image',
            'code': 'testaurant',
            'short_code': 'tsr',
            'description': 'test',
            'about': 'test'
        }

        menu_items = [
            {
                'title': 'Quarter Pounder',
                'description': 'Royal with Cheese'
            },
            {
                'title': 'Grilled Shrimp on the Barbie',
                'description': 'Sprinkled with seasonings and delicately grilled. '
                               'Served with freshly made remoulade sauce.'
            },
            {
                'title': 'California Chicken Salad',
                'description': 'Wood-fire grilled chicken and crumbled Feta cheese atop leafy mixed greens, '
                               'baby spinach, roasted walnuts and diced green apples. '
                               'Tossed in our original vinaigrette. '
            }
        ]

        self.menu_item_template = {
            'title': 'Quarter Pounder',
            'description': 'Royal with Cheese'
        }

        restaurant = self.create_restaurant(self.restaurant_template)
        current_revision = restaurant.current_revision.target

        for mi in menu_items:
            menu_resource = ResourceType.from_result(
                self.g.V(current_revision.id).outE().inV().has('name', RESTAURANT_RESOURCE_TYPE_MENU).next())
            menu_item = self.create_menu_item(template=mi, save=False)
            menu_item.resource_type = MenuItemResourceTypeRelation(source=menu_resource, target=menu_item)
            image, file, mr = self.create_image()

            mr = MediaResource.objects.get(id=mr.id)
            menu_item.image = MenuItemMediaResourceRelation(source=menu_item, target=mr)
            menu_item.save()

        certificate_template = {
            "uri": "example.com",
            "expire_date": datetime.now()
        }

        certificate_file = self.create_certificate_file(template=certificate_template, save=False)
        file_resource = ResourceType.from_result(
            self.g.V(current_revision.id).outE().inV().has('name', RESTAURANT_RESOURCE_TYPE_FILE).next())
        certificate_file.save()

        certificate_file = CertificateFile.from_result(self.g.V(certificate_file.id).next())
        FileResourceTypeRelation(source=file_resource, target=certificate_file).save()

        original_revision = Revision.objects.get(id=current_revision.id)

        return restaurant, original_revision

    def create_revision_with_clone(self):
        restaurant, original_revision = self.create_revision_with_nested_objects()
        new_revision = original_revision.clone()
        cloned_revision = Revision.objects.get(id=new_revision.id)

        return restaurant, original_revision, cloned_revision


class TestModelBulkOperation(element.Vertex):
    field_unique = properties.Property(properties.String)
    integer_field = properties.Property(properties.Integer(positive=True))

    class Meta:
        unique_fields = ('field_unique',)


class TestModelValidator(element.Vertex):
    required_field = properties.Property(properties.String(required=True))
    positive_integer_field = properties.Property(properties.Integer(positive=True))
    positive_float_field = properties.Property(properties.Float(positive=True))
    string_with_max_length = properties.Property(properties.String(max_length=3))
    string_with_min_length = properties.Property(properties.String(min_length=3))
    string_with_length = properties.Property(properties.String(length=5))
    choices_string = properties.Property(properties.String(choices=['first', 'second']))
    choices_float = properties.Property(properties.Float(choices=[1.11, 2.22]))
    choices_integer = properties.Property(properties.Integer(choices=[1, 2]))
    field_unique = properties.Property(properties.String)

    class Meta:
        unique_fields = ('field_unique',)


if __name__ == '__main__':
    unittest.main()
