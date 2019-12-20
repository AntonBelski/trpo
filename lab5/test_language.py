import copy
from uuid import UUID

from app.core.database.exception import ElementError
from app.mos.models import Language
from tests import BasicTestCase


class LanguageTestCase(BasicTestCase):
    def setUp(self):
        super().setUp()

        self.language_template = {
            'code': 'EN',
            'title': 'English'
        }

        self.language_template_second = {
            'code': 'AU',
            'title': 'English (Australia)'
        }

        self.language_template_update = {
            'code': 'EN',
            'title': 'Updated English'
        }

    def create_language(self, language_template):
        language = Language(**language_template)
        language.save()
        return language

    def test_create_language(self):
        language = self.create_language(self.language_template)
        self.assertIsNotNone(language.id)

    def test_read_language(self):
        language = self.create_language(self.language_template)
        search_id = UUID(language.id)
        language_found = Language.objects.get(id=search_id)
        self.assertIsNotNone(language_found)

    def test_update_language(self):
        language = self.create_language(self.language_template)
        search_id = UUID(language.id)
        self.language_template_update.update({'id': search_id})

        language_for_update = Language.objects.get(id=search_id)
        language_for_update.save(**self.language_template_update)

        language_found = Language.objects.get(id=search_id)

        self.assertEqual(
            (self.language_template_update['title'], self.language_template_update['code']),
            (language_found.title, language_found.code)
        )

    def test_delete_language(self):
        language = self.create_language(self.language_template)
        delete_id = UUID(language.id)
        language_for_delete = Language.objects.get(id=delete_id)
        self.assertIsNotNone(language_for_delete)
        deleted = language_for_delete.delete()
        self.assertTrue(deleted)

    def test_create_will_raise_exception_because_of_code_unique_constraint(self):
        with self.assertRaises(ElementError):
            self.create_language(self.language_template)
            self.create_language(self.language_template)

    def test_update_will_raise_exception_because_of_code_unique_constraint(self):
        language_en = self.create_language(self.language_template)
        language_au = self.create_language(self.language_template_second)
        update_props = copy.copy(self.language_template_second)
        update_props.update({'id':language_en.id})
        with self.assertRaises(ElementError):
            language_en.save(**update_props)

