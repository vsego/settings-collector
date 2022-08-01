"""
Loader that grabs settings from Flask's config.
"""

from typing import Any

from .base import SC_LoaderFromDict


class SC_FlaskLoader(SC_LoaderFromDict):
    """
    Loader that grabs settings from Flask's config.
    """

    name_case = str.upper

    @classmethod
    def get_source(cls) -> Any:
        """
        Return dictionary that with settings.
        """
        from flask import current_app  # type: ignore
        return current_app.config  # pragma: no cover
