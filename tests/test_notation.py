import copy
import pickle
import unittest
from collections import defaultdict

from notation import Notation


def module_level_handler():
    pass


class NotationTests(unittest.TestCase):
    def test_constructor_rejects_non_dictionaries(self):
        for annotation in ([], (), "metadata", 42):
            with self.subTest(annotation=annotation):
                with self.assertRaises(TypeError):
                    Notation(annotation)

    def test_constructor_accepts_dictionary_subclasses(self):
        class Metadata(dict):
            pass

        annotation = Metadata(value=1)
        notation = Notation(annotation)
        notation.value = 2

        self.assertEqual(annotation["value"], 2)

    def test_deep_copy_copies_nested_metadata(self):
        original = Notation({"values": [1]})
        duplicate = copy.deepcopy(original)

        duplicate.values.append(2)
        duplicate.extra = True

        self.assertEqual(original.values, [1])
        self.assertEqual(duplicate.values, [1, 2])
        self.assertNotIn("extra", original)

    def test_pickle_round_trip_preserves_metadata_and_attribute_access(self):
        original = Notation({"value": 1})
        restored = pickle.loads(pickle.dumps(original))

        self.assertEqual(restored["value"], 1)
        restored.value = 2

        self.assertEqual(restored["value"], 2)
        self.assertEqual(original.value, 1)

    def test_pickle_round_trip_restores_function_keys_by_reference(self):
        original = Notation()
        original("public", method="GET")(module_level_handler)

        restored = pickle.loads(pickle.dumps(original))

        self.assertIn(module_level_handler, restored)
        self.assertEqual(
            restored[module_level_handler], {0: "public", "method": "GET"}
        )

    def test_default_instances_have_independent_dictionaries(self):
        first = Notation()
        second = Notation()
        third = Notation(None)

        first["value"] = 1

        self.assertEqual(first["value"], 1)
        self.assertNotIn("value", second)
        self.assertNotIn("value", third)

    def test_supplied_dictionary_is_used_directly(self):
        annotation = {"value": 1}
        notation = Notation(annotation)

        notation["value"] = 2
        annotation["other"] = 3

        self.assertIs(vars(notation), annotation)
        self.assertEqual(annotation["value"], 2)
        self.assertEqual(notation["other"], 3)

    def test_shallow_copy_has_an_independent_dictionary(self):
        original = Notation({"value": 1})
        duplicate = copy.copy(original)

        duplicate.value = 2

        self.assertEqual(original.value, 1)
        self.assertEqual(duplicate.value, 2)

    def test_dictionary_subclass_overrides_apply_to_item_access_only(self):
        annotation = defaultdict(int)
        notation = Notation(annotation)

        self.assertEqual(notation["counter"], 0)
        with self.assertRaises(AttributeError):
            _ = notation.missing

        self.assertEqual(dict(annotation), {"counter": 0})

    def test_attribute_access_reads_writes_and_deletes_string_keys(self):
        annotation = {"name": "before"}
        notation = Notation(annotation)

        self.assertEqual(notation.name, "before")
        notation.name = "after"
        self.assertEqual(annotation["name"], "after")

        del notation.name
        self.assertNotIn("name", annotation)
        with self.assertRaises(AttributeError):
            del notation.name

    def test_missing_attribute_raises_attribute_error(self):
        notation = Notation()

        with self.assertRaises(AttributeError):
            _ = notation.missing

    def test_truthiness_follows_the_backing_dictionary(self):
        notation = Notation()

        self.assertFalse(notation)
        notation["value"] = 1

        self.assertTrue(notation)

    def test_missing_item_raises_key_error(self):
        with self.assertRaises(KeyError):
            _ = Notation()["missing"]

    def test_unhashable_keys_raise_type_error(self):
        notation = Notation()
        with self.assertRaises(TypeError):
            _ = notation[[]]
        with self.assertRaises(TypeError):
            notation[[]] = "value"
        with self.assertRaises(TypeError):
            _ = [] in notation

    def test_empty_decorator_retains_function_identity_and_signature_behavior(self):
        notation = Notation()

        def function(value, *, multiplier=2):
            return value * multiplier

        decorated = notation()(function)

        self.assertIs(decorated, function)
        self.assertEqual(notation[function], {})
        self.assertEqual(decorated(3, multiplier=4), 12)

    def test_item_access_and_contains(self):
        notation = Notation()

        notation["answer"] = 42

        self.assertEqual(notation["answer"], 42)
        self.assertIn("answer", notation)
        self.assertNotIn("missing", notation)

    def test_string_and_repr_show_backing_dictionary(self):
        notation = Notation({"name": "value"})

        self.assertEqual(str(notation), "{'name': 'value'}")
        self.assertEqual(
            repr(notation), "Notation(annotation={'name': 'value'})"
        )

    def test_decorator_stores_positional_and_keyword_metadata(self):
        notation = Notation()

        @notation("public", "v1", method="GET")
        def endpoint():
            return "ok"

        self.assertEqual(
            notation[endpoint], {0: "public", 1: "v1", "method": "GET"}
        )
        self.assertEqual(endpoint(), "ok")

    def test_decorator_accepts_self_as_a_metadata_key(self):
        notation = Notation()

        @notation(self="instance")
        def method():
            pass

        self.assertEqual(notation[method], {"self": "instance"})

    def test_decorator_returns_function_and_can_store_multiple_functions(self):
        notation = Notation()

        @notation(role="reader")
        def read():
            pass

        @notation(role="writer")
        def write():
            pass

        self.assertEqual(notation[read], {"role": "reader"})
        self.assertEqual(notation[write], {"role": "writer"})

    def test_methods_are_keyed_by_the_underlying_function(self):
        notation = Notation()

        class Service:
            @notation(route="/items")
            def items(self):
                pass

            @classmethod
            @notation(route="/create")
            def create(cls):
                pass

        service = Service()

        self.assertEqual(notation[Service.items], {"route": "/items"})
        self.assertEqual(notation[service.items.__func__], {"route": "/items"})
        self.assertEqual(notation[Service.create.__func__], {"route": "/create"})
        self.assertNotIn(service.items, notation)

    def test_decorating_same_function_replaces_its_metadata(self):
        notation = Notation()

        def operation():
            pass

        notation(old=True)(operation)
        result = notation(new=True)(operation)

        self.assertIs(result, operation)
        self.assertEqual(notation[operation], {"new": True})


if __name__ == "__main__":
    unittest.main()
