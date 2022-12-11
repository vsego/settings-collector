"""
Loader that grabs settings from CherryPy' config.

Note: I never used CherryPy. This was made based on reading the docs. Ping me
if it's wrong, please.
"""

from copy import deepcopy
from typing import Any

from .base import SC_LoaderFromDict


class SC_CherryPyLoader(SC_LoaderFromDict):
    """
    Loader that grabs settings from CherryPy's config.
    """

    no_settings_exceptions = (ImportError, AttributeError)

    @classmethod
    def get_source(cls) -> Any:
        """
        Return dictionary that with settings.
        """
        import cherrypy  # type: ignore
        result = deepcopy(cherrypy.config)  # pragma: no cover
        result.update(cherrypy.request.app.config)  # pragma: no cover
        return result  # pragma: no cover
