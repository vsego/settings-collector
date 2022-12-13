import unittest.mock

import settings_collector.settings
from settings_collector import (
    SettingsCollector, SC_Setting, SC_SettingsError, SC_Settings,
)

from tests.utils import TestsBase, patch_env


class TestSetting(TestsBase):
    """
    Setting of a value from the code (as opposed to getting it from congig).
    """

    @unittest.mock.patch.dict(
        "settings_collector.sc_settings",
        {"tEsT__fOO": "bard", "TEST__OOF": "food", "tEsT__scOPE__fOO": "bark"},
        clear=True,
    )
    def test_setting(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "tEsT"
            fOO = SC_Setting("bar")
            oof = SC_Setting("rab")

        with patch_env(test_foo="foot"):
            self.assertEqual(my_settings.fOO, "bard")
            self.assertEqual(my_settings("scOPE").fOO, "bark")
            self.assertEqual(my_settings.oof, "rab")

    def test_dict_replaced_sc_settings(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "tEsT"
            fOO = SC_Setting("bar")

        try:
            original = settings_collector.settings.sc_settings
            settings_collector.settings.sc_settings = {"tEsT__fOO": "bard"}
            with self.assertRaises(SC_SettingsError):
                my_settings.fOO
        finally:
            settings_collector.settings.sc_settings = original

    def test_subclass_replaced_sc_settings(self):
        class SC_BogusSettings(SC_Settings):
            instance = None

            def __new__(cls, *args, **kwargs):
                return dict.__new__(cls, *args, **kwargs)

        class my_settings(SettingsCollector):
            class SC_Config:
                prefix = "tEsT"
            fOO = SC_Setting("bar")

        try:
            original = settings_collector.settings.sc_settings
            settings_collector.settings.sc_settings = SC_BogusSettings()
            with self.assertRaises(SC_SettingsError):
                my_settings.fOO
        finally:
            settings_collector.settings.sc_settings = original
