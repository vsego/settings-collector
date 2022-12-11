from copy import copy, deepcopy

from settings_collector import SettingsCollector, SC_Setting

from tests.utils import TestsBase, patch_env


class TestSetting(TestsBase):
    """
    Setting of a value from the code (as opposed to getting it from congig).
    """

    def test_setting(self):
        class my_setting(SettingsCollector):
            foo = SC_Setting("bar")
            not_set = SC_Setting("not set")

        with patch_env(foo="rab", x__foo="beep"):
            self.assertEqual(my_setting.foo, "rab")
            self.assertEqual(my_setting("x").foo, "beep")
            my_setting.foo = "bra"
            my_setting("x").foo = "boop"
            my_setting("y").foo = "bapp"
            self.assertEqual(my_setting.foo, "bra")
            self.assertEqual(my_setting("x").foo, "boop")
            self.assertEqual(my_setting("y").foo, "bapp")

            my_setting.clear_cache()

            self.assertEqual(my_setting.foo, "rab")
            self.assertEqual(my_setting("x").foo, "beep")
            self.assertEqual(my_setting("y").foo, "rab")

            my_setting("a__b").not_set = "is set!"
            self.assertEqual(my_setting.not_set, "not set")
            self.assertEqual(my_setting("x").not_set, "not set")
            self.assertEqual(my_setting("y").not_set, "not set")
            self.assertEqual(my_setting("a").not_set, "not set")
            self.assertEqual(my_setting("b").not_set, "not set")
            self.assertEqual(my_setting("a__b").not_set, "is set!")
            self.assertEqual(my_setting("a__b__c").not_set, "is set!")

    def test_copy(self):
        sc1 = SC_Setting(default={"a": 17})
        sc2 = copy(sc1)
        self.assertIsNot(sc1, sc2)
        self.assertEqual(sc1.default, sc2.default)
        self.assertIs(sc1.default, sc2.default)

    def test_deepcopy(self):
        sc1 = SC_Setting(default={"a": 17})
        sc2 = deepcopy(sc1)
        self.assertIsNot(sc1, sc2)
        self.assertEqual(sc1.default, sc2.default)
        self.assertIsNot(sc1.default, sc2.default)
