from app.mos.models import *

from tests import BasicTestCase, TestUtils


class SlidesTestCase(BasicTestCase, TestUtils):
    def setUp(self):
        super().setUp()
        self.slide_template = {
            'title': 'SlideName'
        }

        self.slide_updated_title = 'UpdatedSlideTitle'

        self.slide_group_template = {
            'title': 'SlideGroupName'
        }

        self.slide_action_template = {
            'action': 'open_category'
        }

    def test_create_slide(self):
        slide = self.create_slide(self.slide_template)
        self.assertIsNotNone(Slide.objects.get(id=slide.id))

    def test_create_slide_group(self):
        slide_group = self.create_slide_group(self.slide_group_template)
        self.assertIsNotNone(SlideGroup.objects.get(id=slide_group.id))

    def test_create_slide_action(self):
        slide_action = self.create_slide_action(self.slide_action_template)
        self.assertIsNotNone(SlideAction.objects.get(id=slide_action.id))

    def test_update_slide(self):
        slide = self.create_slide(self.slide_template)
        slide = Slide.objects.get(id=slide.id)
        self.slide_template.update({'title': self.slide_updated_title})
        slide.save(**self.slide_template)
        updated_slide = Slide.objects.get(id=slide.id)
        self.assertEquals(self.slide_updated_title, slide.title)

    def test_create_slide_group_with_parent(self):
        slide_group = self.create_slide_group(self.slide_group_template, save=False)
        slide = self.create_slide(self.slide_template)
        slide_group.slides = [MenuCategoryItemRelation(source=slide_group, target=slide)]
        slide_group.save()
        new_slide_group = SlideGroup.objects.get(id=slide_group.id)
        self.assertIsNotNone(new_slide_group.slides[0])
