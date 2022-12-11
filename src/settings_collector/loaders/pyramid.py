"""
Loader that grabs settings from Pyramid's config.

Note: I never used Pyramid. This was made based on reading the docs. Ping me
if it's wrong, please.
"""

from typing import Any

from .base import SC_LoaderFromDict


class SC_PyramidLoader(SC_LoaderFromDict):
    """
    Loader that grabs settings from Pyramid's config.
    """

    @classmethod
    def get_source(cls) -> Any:
        """
        Return dictionary that with settings.
        """
        from pyramid import registry  # type: ignore
        return registry.config  # pragma: no cover
