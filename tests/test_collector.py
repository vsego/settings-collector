import unittest.mock

from settings_collector import (
    SettingsCollector, SC_WeirdBugError, SC_LoaderBase, SC_ConfigError,
)

from tests.utils import TestsBase


class TestBasicFunctionality(TestsBase):

    def test_weird_bugs(self):
        for what in ("root", "root.SC_Data.scopes"):
            with unittest.mock.patch(
                f"settings_collector.SettingsCollector.SC_Data.{what}",
                None,
            ):
                with self.assertRaises(SC_WeirdBugError):
                    SettingsCollector._get_scope("scope")

    def test_name_case(self):
        source_name = "sOmEnAmE"
        for name_case, is_ok, result in (
            (None, True, source_name),
            (str.lower, True, source_name.lower()),
            ("str.lower", False, SC_ConfigError),
        ):
            with unittest.mock.patch(
                "settings_collector.SC_LoaderBase.name_case",
                name_case,
            ):
                if is_ok:
                    self.assertEqual(
                        SC_LoaderBase._get_source_name(source_name),
                        result,
                    )
                else:
                    with self.assertRaises(result):
                        SC_LoaderBase._get_source_name(source_name)
