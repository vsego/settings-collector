from settings_collector import SettingsCollector, SC_Setting

from tests.utils import TestsBase, patch_env


class TestScopes(TestsBase):

    def test_scope(self):
        class my_settings(SettingsCollector):
            defaults = {"simple1": "foo"}
            simple2 = SC_Setting("bar")
            int1 = SC_Setting(17, value_type=int)
            int2 = SC_Setting(19, value_type=int)

        with patch_env(
            simple1="food", x__simple1="fooled",
            y__simple2="barred",
            int1=13, x__int1=11,
            x__int2=23, y__int2=29,
        ):
            # Root
            self.assertEqual(my_settings.simple1, "food")
            self.assertEqual(my_settings.simple2, "bar")
            self.assertEqual(my_settings.int1, 13)
            self.assertEqual(my_settings.int2, 19)

            # Scope: x
            self.assertEqual(my_settings("x").simple1, "fooled")
            self.assertEqual(my_settings("x").simple2, "bar")
            self.assertEqual(my_settings("x").int1, 11)
            self.assertEqual(my_settings("x").int2, 23)

            # Scope: y
            self.assertEqual(my_settings("y").simple1, "food")
            self.assertEqual(my_settings("y").simple2, "barred")
            self.assertEqual(my_settings("y").int1, 13)
            self.assertEqual(my_settings("y").int2, 29)

    def test_deep_scope(self):
        class my_settings(SettingsCollector):
            foo = SC_Setting("foo")

        with patch_env(
            foo="empty", x__foo="x", x__y__foo="xy", x__y__z__q__foo="xyzq",
        ):
            self.assertEqual(my_settings.foo, "empty")
            self.assertEqual(my_settings("x").foo, "x")
            self.assertEqual(my_settings("x__y").foo, "xy")
            self.assertEqual(my_settings("x__y__z").foo, "xy")
            self.assertEqual(my_settings("x__y__z__q").foo, "xyzq")
            self.assertEqual(my_settings("bar").foo, "empty")

    def test_two_scopes(self):
        class my_settings(SettingsCollector):
            foo = SC_Setting("foo")

        with patch_env(x__foo="x"):
            self.assertEqual(my_settings.foo, "foo")
            self.assertEqual(my_settings("x").foo, "x")
            self.assertEqual(my_settings("bar").foo, "foo")
            self.assertEqual(my_settings("bar__x").foo, "foo")
