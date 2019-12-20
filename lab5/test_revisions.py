from graphene.test import Client

from app.mos.models import Revision
from app.mos.schema import schema
from tests import BasicTestCase, TestUtils


class RevisionTestCase(BasicTestCase, TestUtils):
    excluded_properties = ()

    def setUp(self):
        super().setUp()

        self.g = self.db.get_traversal()

        self.restaurant, self.original_revision = self.create_revision_with_nested_objects()
        new_revision = self.original_revision.clone()
        self.cloned_revision = Revision.objects.get(id=new_revision.id)

    def test_equalities_of_objects(self):
        old_revision_objects = self.original_revision._get_objects_to_clone(self.g, self.original_revision.id)
        from gremlin_python.process.traversal import T

        for old_vert in old_revision_objects[0]['vertices']:
            v1_props = self.g.V().has('cloned_from', old_vert.id).valueMap(True).toList()[0]
            v2_props = self.g.V(old_vert.id).valueMap(True).toList()[0]

            for prop in v2_props:
                if isinstance(prop, T) or prop in ('cloned_from', 'version'):
                    continue
                self.assertEqual(v1_props.get(prop), v2_props.get(prop))

        for old_edge in old_revision_objects[0]['edges']:
            e1_props_list = self.g.E().has('cloned_from', old_edge.id).valueMap(True).toList()

            if e1_props_list:
                e1_props = e1_props_list[0]
            else:
                continue

            e2_props = self.g.E()(old_edge.id).valueMap(True).toList()[0]

            for prop in e2_props:
                if isinstance(prop, T) or prop in ('cloned_from', 'version'):
                    continue
                self.assertEqual(e1_props.get(prop), e2_props.get(prop))

    def test_cloned_revision_has_parent_relation(self):
        self.assertEqual(self.cloned_revision.parent.source.id, self.original_revision.id)

    def test_image_file_not_cloned(self):
        from app.mos.models.file import ImageFile
        self.assertEqual(3, self.g.V().hasLabel(ImageFile.__label__).count().next())

    def test_image_has_one_file_relation(self):
        from app.mos.models.file import ImageFile, FileRelation
        self.assertEqual(3, self.g.V().hasLabel(ImageFile.__label__).outE().hasLabel(
            FileRelation.__label__).count().next())

    def test_image_has_two_media_resource_relations(self):
        from app.mos.models.file import ImageFile, MediaResourceRelation
        self.assertEqual(6, self.g.V().hasLabel(ImageFile.__label__).inE().hasLabel(
            MediaResourceRelation.__label__).count().next())


class RevisionMutationsTest(BasicTestCase, TestUtils):
    def setUp(self):
        super().setUp()
        self.g = self.db.get_traversal()
        self.restaurant, self.original_revision, self.cloned_revision = self.create_revision_with_clone()

    def test_switch_revision_mutation(self):
        client = Client(schema)

        executed = client.execute('''
            mutation switchRevision($revision: RevisionSwitchInput!){
              switch_revision(revision:$revision){
                id,
                version
              }
            }
        ''', variable_values={'revision': {'restaurant': self.restaurant.id, 'revision': self.cloned_revision.id}})

        assert executed == {
            "data": {
                "switch_revision": {
                    "id": str(self.cloned_revision.id),
                    "version": str(self.cloned_revision.version)
                }
            }
        }

    def test_create_revision_mutation(self):
        client = Client(schema)

        executed = client.execute('''
            mutation createRevision($revision: RevisionCreateInput!){
              create_revision(revision:$revision){
                id,
                version
              }
            }
        ''', variable_values={'revision': {'restaurant': self.restaurant.id}})

        restaurant = self.restaurant.objects.get(self.restaurant.id)

        assert executed == {
            "data": {
                "create_revision": {
                    "id": str(restaurant.current_revision.target.id),
                    "version": restaurant.current_revision.target.version
                }
            }
        }
