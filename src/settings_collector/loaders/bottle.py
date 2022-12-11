"""
Loader that grabs settings from Bottle's config.

Note: I never used Bottle. This was made based on reading the docs. Ping me
if it's wrong, please.
"""

from typing import Any

from .base import SC_LoaderFromDict


class SC_BottleLoader(SC_LoaderFromDict):
    """
    Loader that grabs settings from Bottle's config.
    """

    @classmethod
    def get_source(cls) -> Any:
        """
        Return dictionary that with settings.
        """
        import bottle  # type: ignore
        return bottle.default_app().config  # pragma: no cover
