from settings_collector import (
    SettingsCollector, SC_Setting, SC_undef, SC_ConfigError,
)

from tests.utils import TestsBase, patch_env


class TestBasicFunctionality(TestsBase):

    def _run_test_no_default_missing(self, field_name):
        class my_settings(SettingsCollector):
            defaults = {"simple1": "foo", "simple2": SC_undef}
            simple3 = SC_Setting("bar")
            simple4 = SC_Setting()

        # Greedy loading means that fetching of _any_ field will fail if some
        # value is missing.
        with patch_env(simple1="food", simple3="bard"):
            with self.assertRaises(ValueError):
                getattr(my_settings, field_name)

    def test_no_default_missing(self):
        for field_name in ("simple1", "simple2", "simple3", "simple4"):
            self._run_test_no_default_missing(field_name)

    def test_no_default_lazy(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                greedy_load = False
            defaults = {"simple1": "foo", "simple2": SC_undef}
            simple3 = SC_Setting("bar")
            simple4 = SC_Setting()

        with patch_env(simple1="food", simple3="bard"):
            self.assertEqual(my_settings.simple1, "food")
            with self.assertRaises(ValueError):
                my_settings.simple2
            self.assertEqual(my_settings.simple3, "bard")
            with self.assertRaises(ValueError):
                my_settings.simple4

    def test_no_default_ok(self):
        class my_settings(SettingsCollector):
            defaults = {"simple1": "foo", "simple2": SC_undef}
            simple3 = SC_Setting("bar")
            simple4 = SC_Setting()

        with patch_env(simple2="food", simple4="bard"):
            self.assertEqual(my_settings.simple1, "foo")
            self.assertEqual(my_settings.simple2, "food")
            self.assertEqual(my_settings.simple3, "bar")
            self.assertEqual(my_settings.simple4, "bard")

    def test_prefix(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "test"
                sep = "__"
            defaults = {"simple1": "foo"}
            simple2 = SC_Setting("bar")

        with patch_env(test__simple1="food", test__simple2="bard"):
            self.assertEqual(my_settings.simple1, "food")
            self.assertEqual(my_settings.simple2, "bard")

    def test_prefix_lazy(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                greedy_load = False
                prefix = "test"
                sep = "__"
            defaults = {"simple1": "foo"}
            simple2 = SC_Setting("bar")

        with patch_env(simple1="food", simple2="bard"):
            self.assertEqual(my_settings.simple1, "foo")
            self.assertEqual(my_settings.simple2, "bar")

        with patch_env(test__simple1="food", test__simple2="bard"):
            self.assertEqual(my_settings.simple1, "food")
            self.assertEqual(my_settings.simple2, "bard")

    def test_prefix_greedy(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                greedy_load = True
                prefix = "test"
                sep = "__"
            defaults = {"simple1": "foo"}
            simple2 = SC_Setting("bar")

        with patch_env(simple1="food", simple2="bard"):
            self.assertEqual(my_settings.simple1, "foo")
            self.assertEqual(my_settings.simple2, "bar")

        with patch_env(test__simple1="food", test__simple2="bard"):
            self.assertEqual(my_settings.simple1, "foo")
            self.assertEqual(my_settings.simple2, "bar")

    def test_prefix_greedy_clear_cache(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "test"
                sep = "__"
            defaults = {"simple1": "foo"}
            simple2 = SC_Setting("bar")

        with patch_env(simple1="food", simple2="bard"):
            self.assertEqual(my_settings.simple1, "foo")
            self.assertEqual(my_settings.simple2, "bar")

        my_settings.clear_cache()

        with patch_env(test__simple1="food", test__simple2="bard"):
            self.assertEqual(my_settings.simple1, "food")
            self.assertEqual(my_settings.simple2, "bard")

    def test_cast(self):
        class my_settings(SettingsCollector):
            simple1 = SC_Setting(value_type=str)
            simple2 = SC_Setting(value_type=int)

        with patch_env(simple1="food", simple2="17"):
            self.assertEqual(my_settings.simple1, "food")
            self.assertEqual(my_settings.simple2, 17)

    def test_cached(self):
        class my_settings(SettingsCollector):
            defaults = {"simple1": "foo"}
            simple2 = SC_Setting("bar")
            int1 = SC_Setting(17, value_type=int)
            int2 = SC_Setting(19, value_type=int)
            int3 = SC_Setting(23.29, value_type=int)
            int4 = SC_Setting(31, value_type=int)

        with patch_env(simple1="food", int2=13, int4=37.41):
            self.assertEqual(my_settings.simple1, "food")
            self.assertEqual(my_settings.simple2, "bar")
            self.assertEqual(my_settings.int1, 17)
            self.assertEqual(my_settings.int2, 13)
            self.assertEqual(my_settings.int3, 23.29)
            self.assertEqual(my_settings.int4, 31)

        with patch_env(simple1="new", int2=11, int3=43):
            self.assertEqual(my_settings.simple1, "food")
            self.assertEqual(my_settings.simple2, "bar")
            self.assertEqual(my_settings.int1, 17)
            self.assertEqual(my_settings.int2, 13)
            self.assertEqual(my_settings.int3, 23.29)

        my_settings.clear_cache()

        with patch_env(int3=43):
            self.assertEqual(my_settings.int3, 43)

    def test_not_cached(self):
        class my_settings(SettingsCollector):
            nc1 = SC_Setting("default", no_cache=True)
            nc2 = SC_Setting("default", no_cache=True)
            nc3 = SC_Setting("default", no_cache=True)

        with patch_env(nc1="not default"):
            self.assertEqual(my_settings.nc1, "not default")
            self.assertEqual(my_settings.nc2, "default")
            self.assertEqual(my_settings.nc3, "default")

        with patch_env(nc1="also not default", nc2="maybe default?"):
            self.assertEqual(my_settings.nc1, "also not default")
            self.assertEqual(my_settings.nc2, "maybe default?")
            self.assertEqual(my_settings.nc3, "default")

    def test_name_case(self):
        class my_settings(SettingsCollector):
            simple1 = SC_Setting("default1")
            simple2 = SC_Setting("default2")

        with patch_env(simple1="modified1", SIMPLE2="modified2", _upper=False):
            self.assertEqual(my_settings.simple1, "default1")
            self.assertEqual(my_settings.simple2, "modified2")

    def _get_bad_name_1(self):
        class my_settings(SettingsCollector):
            SC_foo = SC_Setting()

    def _get_bad_name_2(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                sep = "xxx"

            xxxFoo = SC_Setting()

    def test_bad_names(self):
        self.assertRaises(SC_ConfigError, self._get_bad_name_1)
        self.assertRaises(SC_ConfigError, self._get_bad_name_2)

    def test_preserve_defaults_1(self):
        class my_settings(SettingsCollector):
            defaults = SC_Setting()  # not a special dict!!!

        with patch_env(defaults="ze defaults..."):
            self.assertEqual(my_settings.defaults, "ze defaults...")

    def test_preserve_defaults_2(self):
        class my_settings(SettingsCollector):
            defaults = {"defaults": "default"}

        with patch_env(defaults="ze defaults..."):
            self.assertEqual(my_settings.defaults, "ze defaults...")

    def test_setting_invalid_value(self):
        class my_settings(SettingsCollector):
            foo = SC_Setting()

        with self.assertRaises(AttributeError):
            my_settings.bar = 17
