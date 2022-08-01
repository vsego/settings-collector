"""
Loader that grabs settings from TurboGears' config.

Note: I never used TurboGears. This was made based on reading the docs and TG's
source on Github. Ping me if it's wrong, please.
"""

from typing import Any

from .base import SC_LoaderFromDict


class SC_TurboGearsLoader(SC_LoaderFromDict):
    """
    Loader that grabs settings from TurboGears's config.
    """

    @classmethod
    def get_source(cls) -> Any:
        """
        Return dictionary that with settings.
        """
        import turbogears  # type: ignore
        return turbogears.config  # pragma: no cover
