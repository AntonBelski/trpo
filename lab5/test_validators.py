import copy
from uuid import UUID

from app.core.database.exception import ValidationError, ElementError
from tests import BasicTestCase, TestModelValidator


class ValidatorsTestCase(BasicTestCase):
    def setUp(self):
        super().setUp()
        self.obj_template = {
            'required_field': 'field',
            'positive_integer_field': 10,
            'positive_float_field': 1.11,
            'string_with_max_length': 's',
            'string_with_min_length': 'test',
            'string_with_length': 'fivee',
            'choices_string': 'first',
            'choices_float': 1.11,
            'choices_integer': 1,
            'field_unique': 'unique',
        }

    def create_obj(self):
        obj = TestModelValidator(**self.obj_template)
        obj.save()
        return obj

    def test_create_successfully(self):
        obj = self.create_obj()
        self.assertIsNotNone(obj.id)

    def test_create_without_required_field(self):
        del self.obj_template['required_field']
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_with_only_required_fields(self):
        # unique is also required
        obj_template_copy = copy.copy(self.obj_template)
        for key in self.obj_template:
            if key not in ('required_field', 'field_unique'):
                del obj_template_copy[key]
        self.obj_template = obj_template_copy
        obj = self.create_obj()
        self.assertIsNotNone(obj.id)

    def test_create_raises_exception_positive_integer_field(self):
        self.obj_template['positive_integer_field'] = -10
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_raises_exception_positive_float_field(self):
        self.obj_template['positive_float_field'] = -1.11
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_raises_exception_string_max_length(self):
        # max is 3
        self.obj_template['string_with_max_length'] = 'more than three'
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_raises_exception_string_min_length(self):
        # min is 3
        self.obj_template['string_with_min_length'] = 'lt'
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_raises_exception_string_fixed_length(self):
        # length is 5
        self.obj_template['string_with_length'] = 'less'
        with self.assertRaises(ValidationError):
            self.create_obj()

        self.obj_template['string_with_length'] = 'more than five'
        with self.assertRaises(ValidationError):
            self.create_obj()

        self.obj_template['string_with_length'] = 'fives'
        obj = self.create_obj()
        self.assertIsNotNone(obj.id)

    def test_create_raises_exception_string_choices(self):
        self.obj_template['choices_string'] = 'third'
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_raises_exception_float_choices(self):
        self.obj_template['choices_float'] = 3.33
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_raises_exception_integer_choices(self):
        self.obj_template['choices_integer'] = 3
        with self.assertRaises(ValidationError):
            self.create_obj()

    def test_create_raises_exception_unique_constraint(self):
        first_obj = self.create_obj()
        with self.assertRaises(ElementError):
            self.create_obj()

        self.obj_template['field_unique'] = 'second_unique'
        second_obj = self.create_obj()
        self.assertIsNotNone(second_obj.id)

    def test_update_raises_exception_positive_integer_field(self):
        obj = self.create_obj()
        self.obj_template.update({'positive_integer_field': -10, 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)

    def test_update_raises_exception_positive_float_field(self):
        obj = self.create_obj()
        self.obj_template.update({'positive_float_field': -1.11, 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)

    def test_update_raises_exception_string_max_length(self):
        # max is 3
        obj = self.create_obj()
        self.obj_template.update({'string_with_max_length': 'more than three', 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)

    def test_update_raises_exception_string_min_length(self):
        # min is 3
        obj = self.create_obj()
        self.obj_template.update({'string_with_min_length': 'lt', 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)

    def test_update_raises_exception_string_fixed_length(self):
        # length is 5
        obj = self.create_obj()
        self.obj_template.update({'string_with_length': 'less', 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)

        self.obj_template.update({'string_with_length': 'more than five', 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)

    def test_update_raises_exception_string_choices(self):
        obj = self.create_obj()
        self.obj_template.update({'choices_string': 'third', 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)
        self.obj_template.update({'choices_string': 'second'})
        obj.save(**self.obj_template)
        self.assertEqual(self.obj_template['choices_string'], obj.choices_string)

    def test_update_raises_exception_float_choices(self):
        obj = self.create_obj()
        self.obj_template.update({'choices_float': 3.33, 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)
        self.obj_template.update({'choices_float': 2.22})
        obj.save(**self.obj_template)
        self.assertEqual(self.obj_template['choices_float'], obj.choices_float)

    def test_update_raises_exception_integer_choices(self):
        obj = self.create_obj()
        self.obj_template.update({'choices_integer': 3, 'id': UUID(obj.id)})
        with self.assertRaises(ValidationError):
            obj.save(**self.obj_template)
        self.obj_template.update({'choices_integer': 2})
        obj.save(**self.obj_template)
        self.assertEqual(self.obj_template['choices_integer'], obj.choices_integer)

    def test_update_raises_exception_unique_constraint(self):
        first_obj = self.create_obj()

        self.obj_template['field_unique'] = 'second_unique'
        second_obj = self.create_obj()

        with self.assertRaises(ElementError):
            first_obj.save(**self.obj_template)
