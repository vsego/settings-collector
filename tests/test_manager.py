from typing import Iterable, Optional, Any
import unittest.mock

from settings_collector import (
    SettingsCollector, SC_LoaderBase, SC_LoadersManager, SC_ConfigError,
)

from tests.utils import TestsBase


class _TestLoAder(SC_LoaderBase):

    @classmethod
    def get_settings(
        cls, prefix: str, settings_names: Iterable[str],
    ) -> Optional[dict[str, Any]]:
        return {"a": 11, "b": 13}


class _TestLoBder(SC_LoaderBase):

    @classmethod
    def get_settings(
        cls, prefix: str, settings_names: Iterable[str],
    ) -> Optional[dict[str, Any]]:
        return {"a": 17, "c": 19}


class TestManager(TestsBase):

    def test_get_loaders_include(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                loaders = ("loAder", "loCder")
                exclude = False

        with unittest.mock.patch(
            "settings_collector.SC_LoadersManager._loaders",
            {"loAder": _TestLoAder, "loBder": _TestLoBder},
        ):
            result = list(SC_LoadersManager._get_loaders(my_settings))
        self.assertEqual(result, [_TestLoAder])

    def test_get_loaders_exclude(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                loaders = ("loAder", "loCder")
                exclude = True

        with unittest.mock.patch(
            "settings_collector.SC_LoadersManager._loaders",
            {"loAder": _TestLoAder, "loBder": _TestLoBder},
        ):
            result = list(SC_LoadersManager._get_loaders(my_settings))
        self.assertEqual(result, [_TestLoBder])

    def test_get_loaders_include_nothing(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                loaders = tuple()
                exclude = False

        with unittest.mock.patch(
            "settings_collector.SC_LoadersManager._loaders",
            {"loAder": _TestLoAder, "loBder": _TestLoBder},
        ):
            with self.assertRaises(ValueError):
                list(SC_LoadersManager._get_loaders(my_settings))

    def test_get_loaders_include_only_unknown(self):
        class my_settings(SettingsCollector):
            class SC_Config:
                loaders = ("loaCder", "loaDder")
                exclude = False

        with unittest.mock.patch(
            "settings_collector.SC_LoadersManager._loaders",
            {"loAder": _TestLoAder, "loBder": _TestLoBder},
        ):
            with self.assertRaises(SC_ConfigError):
                list(SC_LoadersManager._get_loaders(my_settings))

    @unittest.mock.patch("settings_collector.SC_LoadersManager._get_loaders")
    def test_get_settings_load_all(self, mock_get_loaders):
        class my_settings(SettingsCollector):
            class SC_Config:
                load_all = True

        mock_get_loaders.return_value = (
            loader for loader in (_TestLoAder, _TestLoBder)
        )
        expected = {"a": 17, "b": 13, "c": 19}

        result = SC_LoadersManager.get_settings(my_settings)

        self.assertEqual(result, expected)
