"""
Loader that grabs settings from environment variables.
"""

from typing import Any

from .base import SC_LoaderFromDict


class SC_EnvironLoader(SC_LoaderFromDict):
    """
    Loader that grabs settings from environment variables.
    """

    priority = -171923
    enabled = False
    name_case = str.upper

    @classmethod
    def get_source(cls) -> Any:
        """
        Return dictionary that with settings.
        """
        import os
        return os.environ
