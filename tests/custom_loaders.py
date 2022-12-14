"""
Mock loaders.

This mimic a framework that uses inverse case names. So, if you want a setting
called `Foo` in scope `Scope` and with prefix `SCt`, the framework will know it
as `scT__sCOPE__fOO`. It's ridiculous, but the purpose here is just to test
custom loaders.
"""

from typing import Any

from settings_collector import (
    SC_LoaderFromAttribs, SC_LoaderFromDict, SC_LoaderBase,
)


MOCK_LOADER_SETTINGS = {"foo": "bar"}
MOCK_LOW_PRIORITY_LOADER_SETTINGS = {
    "common": "common low", "low_only": "low",
}
MOCK_HIGH_PRIORITY_LOADER_SETTINGS = {
    "common": "common high", "high_only": "high",
}


class MockLoaderException(Exception):
    pass


class SC_MockLoader(SC_LoaderBase):

    enabled = False

    @classmethod
    def load_settings(
        cls, prefix: str, settings_names: list[str],
    ) -> tuple[dict[str, Any], bool]:
        if prefix:
            raise MockLoaderException(prefix)
        else:
            return MOCK_LOADER_SETTINGS, True


class SC_MockLowPriorityLoader(SC_LoaderBase):

    enabled = False
    priority = -17

    @classmethod
    def load_settings(
        cls, prefix: str, settings_names: list[str],
    ) -> tuple[dict[str, Any], bool]:
        return MOCK_LOW_PRIORITY_LOADER_SETTINGS, True


class SC_MockHighPriorityLoader(SC_LoaderBase):

    enabled = False
    priority = 17

    @classmethod
    def load_settings(
        cls, prefix: str, settings_names: list[str],
    ) -> tuple[dict[str, Any], bool]:
        return MOCK_HIGH_PRIORITY_LOADER_SETTINGS, True


class SC_TestAttrLoader(SC_LoaderFromAttribs):

    name_case = str.swapcase

    @classmethod
    def get_source(cls) -> Any:
        """
        Return object that has settings set as attributes.
        """
        # type: ignore
        from settings_collector import _sct_attr_settings  # type: ignore
        return _sct_attr_settings


class SC_TestDictLoader(SC_LoaderFromDict):

    name_case = str.swapcase

    @classmethod
    def get_source(cls) -> Any:
        """
        Return object that has settings set as attributes.
        """
        # type: ignore
        from settings_collector import _sct_dict_settings  # type: ignore
        return _sct_dict_settings
