import unittest.mock

from settings_collector import SettingsCollector

# WARNING: `tests.custom_loaders` must be imported even if you don't use
# anything from it. That gets the mock loaders created and registered.
from tests.custom_loaders import (
    MOCK_LOADER_SETTINGS, SC_MockLoader, MockLoaderException,
    SC_TestAttrLoader,
)
from tests.utils import TestsBase


class TestLoaderBase(TestsBase):

    def test_get_settings_enabled(self):
        for enabled, expected in ((True, MOCK_LOADER_SETTINGS), (False, None)):
            with unittest.mock.patch(
                "tests.custom_loaders.SC_MockLoader.enabled", enabled,
            ):
                result = SC_MockLoader.get_settings("", tuple())
            self.assertEqual(result, expected)

    @unittest.mock.patch("tests.custom_loaders.SC_MockLoader.enabled", True)
    def test_get_settings_unexpected_exception(self):
        with self.assertRaises(MockLoaderException):
            SC_MockLoader.get_settings("error", tuple())


class TestCustomAttrLoader(TestsBase):

    def setUp(self):
        class _sct_attr_settings:
            scT__fOO = "bard"
            scT__sCOPE__fOO = "barman"

        import settings_collector
        settings_collector._sct_attr_settings = _sct_attr_settings
        super().setUp()

    def tearDown(self):
        import settings_collector
        del settings_collector._sct_attr_settings
        super().tearDown()

    def test_custom_loader(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "SCt"
                greedy_load = False
            defaults = {"Foo": "default"}

        self.assertEqual(my_settings.Foo, "bard")
        self.assertEqual(my_settings("Scope").Foo, "barman")

    def test_missing_attribute(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "SCt"
                greedy_load = False
            defaults = {"Foo": "default"}

        self.assertEqual(
            SC_TestAttrLoader.load_settings("scT__", ["Foo", "Missing"]),
            ({"Foo": "bard"}, True),
        )


class TestCustomDictLoader(TestsBase):

    def setUp(self):
        _sct_dict_settings = dict(
            scT__fOO="bard",
            scT__sCOPE__fOO="barman",
        )
        import settings_collector
        settings_collector._sct_dict_settings = _sct_dict_settings
        super().setUp()

    def tearDown(self):
        import settings_collector
        del settings_collector._sct_dict_settings
        super().tearDown()

    def test_custom_loader(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "SCt"
                greedy_load = False
            defaults = {"Foo": "default"}

        self.assertEqual(my_settings.Foo, "bard")
        self.assertEqual(my_settings("Scope").Foo, "barman")


class TestLoaderPriority(TestsBase):

    @unittest.mock.patch(
        "tests.custom_loaders.SC_MockLowPriorityLoader.enabled", True,
    )
    @unittest.mock.patch(
        "tests.custom_loaders.SC_MockHighPriorityLoader.enabled", True,
    )
    def test_loader_priority_load_all_true(self):

        class my_settings(SettingsCollector):
            class SC_Config:
                load_all = True
            defaults = {
                "common": "common default",
                "low_only": "low default",
                "high_only": "high default",
                "neither": "neither default",
            }

        self.assertEqual(my_settings.common, "common high")
        self.assertEqual(my_settings.low_only, "low")
        self.assertEqual(my_settings.high_only, "high")
        self.assertEqual(my_settings.neither, "neither default")

    @unittest.mock.patch(
        "tests.custom_loaders.SC_MockLowPriorityLoader.enabled", True,
    )
    @unittest.mock.patch(
        "tests.custom_loaders.SC_MockHighPriorityLoader.enabled", True,
    )
    def test_loader_priority_load_all_false(self):

        class my_settings(SettingsCollector):
            class SC_Config:
                load_all = False
            defaults = {
                "common": "common default",
                "low_only": "low default",
                "high_only": "high default",
                "neither": "neither default",
            }

        self.assertEqual(my_settings.common, "common high")
        self.assertEqual(my_settings.low_only, "low default")
        self.assertEqual(my_settings.high_only, "high")
        self.assertEqual(my_settings.neither, "neither default")
