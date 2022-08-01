from settings_collector import SettingsCollector, SC_Setting

from tests.utils import TestsBase, patch_env


class TestTwoSettingsCollectors(TestsBase):

    def test_two_settings_collectors(self):
        class my_settings_1(SettingsCollector):
            class SC_Config:
                prefix = "one"
            simple1 = SC_Setting()
            simple2 = SC_Setting()

        class my_settings_2(SettingsCollector):
            class SC_Config:
                prefix = "two"
            simple2 = SC_Setting()
            simple3 = SC_Setting()

        with patch_env(
            one__simple1="food", one__simple2="bard", one__simple3="nein",
            two__simple1="nope", two__simple2="foot", two__simple3="bark",
        ):
            self.assertEqual(my_settings_1.simple1, "food")
            self.assertEqual(my_settings_1.simple2, "bard")
            self.assertEqual(my_settings_2.simple2, "foot")
            self.assertEqual(my_settings_2.simple3, "bark")
