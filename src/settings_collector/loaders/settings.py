"""
Loader that grabs settings from `sc_settings`.
"""

from typing import Any

from ..exceptions import SC_SettingsError
from .base import SC_LoaderFromDict


class SC_SettingsLoader(SC_LoaderFromDict):
    """
    Loader that grabs settings from `sc_settings`.
    """

    priority = 171923

    @classmethod
    def get_source(cls) -> Any:
        """
        Return dictionary that with settings.
        """
        from ..settings import SC_Settings, sc_settings
        if type(sc_settings) is not SC_Settings:
            raise SC_SettingsError(
                "settings_collector.sc_settings can only be modified, but it"
                " must not be replaced",
            )
        return sc_settings
