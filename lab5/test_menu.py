from app.mos.models import *
from app.mos.models import ModifierGroupItemRelation
from tests import BasicTestCase, TestUtils


class MenuTestCase(BasicTestCase, TestUtils):
    def setUp(self):
        super().setUp()

        self.modifier_updated_title = 'Salsa'

        self.mod_group_updated_title = 'Updated Dressings'

        self.modifier_template = {
            'title': 'Ranch',
            'description': 'description'
        }

        self.mod_group_template = {
            'title': 'Dressings'
        }

        self.menu_item_updated_title = 'Royal with Cheese'

        self.menu_category_updated_title = 'Updated Burgers'

        self.menu_item_template = {
            'title': 'Quarter Pounder',
            'description': 'Royal with Cheese'
        }

        self.menu_category_template = {
            'title': 'Burgers'
        }

    def test_create_modifier(self):
        modifier = self.create_modifier(self.modifier_template)
        self.assertIsNotNone(Modifier.objects.get(id=modifier.id))

    def test_create_mod_group(self):
        mod_group = self.create_mod_group(self.mod_group_template)
        self.assertIsNotNone(ModifierGroup.objects.get(id=mod_group.id))

    def test_update_modifier(self):
        modifier = self.create_modifier(self.modifier_template)
        modifier = Modifier.objects.get(id=modifier.id)
        self.modifier_template.update({'title': self.modifier_updated_title})
        modifier.save(**self.modifier_template)
        updated_modifier = Modifier.objects.get(id=modifier.id)
        self.assertEquals(self.modifier_updated_title, updated_modifier.title)

    def test_update_mod_group(self):
        mod_group = self.create_mod_group(self.mod_group_template)
        mod_group = ModifierGroup.objects.get(id=mod_group.id)
        self.mod_group_template.update({'title': self.mod_group_updated_title})
        mod_group.save(**self.mod_group_template)
        updated_mod_group = ModifierGroup.objects.get(id=mod_group.id)
        self.assertEquals(self.mod_group_updated_title, updated_mod_group.title)

    def test_create_mod_group_with_modifier(self):
        mod_group = self.create_mod_group(self.mod_group_template, save=False)
        modifier = self.create_modifier(self.modifier_template)
        mod_group.modifiers = [ModifierGroupItemRelation(source=mod_group, target=modifier)]
        mod_group.save()
        new_mod_group = ModifierGroup.objects.get(id=mod_group.id)
        self.assertIsNotNone(new_mod_group.modifiers)

    def test_create_menu_item(self):
        menu_item = self.create_menu_item(self.menu_item_template)
        self.assertIsNotNone(MenuItem.objects.get(id=menu_item.id))

    def test_create_menu_category(self):
        menu_category = self.create_menu_category(self.menu_category_template)
        self.assertIsNotNone(MenuCategory.objects.get(id=menu_category.id))

    def test_update_menu_item(self):
        menu_item = self.create_menu_item(self.menu_item_template)
        menu_item = MenuItem.objects.get(id=menu_item.id)
        self.menu_item_template.update({'title': self.menu_item_updated_title})
        menu_item.save(**self.menu_item_template)
        updated_menu_item = MenuItem.objects.get(id=menu_item.id)
        self.assertEquals(self.menu_item_updated_title, updated_menu_item.title)

    def test_update_menu_category(self):
        menu_category = self.create_menu_category(self.menu_category_template)
        menu_category = MenuCategory.objects.get(id=menu_category.id)
        self.menu_category_template.update({'title': self.menu_category_updated_title})
        menu_category.save(**self.menu_category_template)
        updated_menu_category = MenuCategory.objects.get(id=menu_category.id)
        self.assertEquals(self.menu_category_updated_title, updated_menu_category.title)

    def test_create_menu_category_with_menu_item(self):
        menu_category = self.create_menu_category(self.menu_category_template, save=False)
        menu_item = self.create_menu_item(self.menu_item_template)
        menu_category.menu_items = [MenuCategoryItemRelation(source=menu_category, target=menu_item)]
        menu_category.save()
        new_menu_category = MenuCategory.objects.get(id=menu_category.id)
        self.assertIsNotNone(new_menu_category.menu_items)
