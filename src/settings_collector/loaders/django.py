"""
Settings loader for Django.
"""

from typing import Any

from .base import SC_LoaderFromAttribs


class SC_DjangoLoader(SC_LoaderFromAttribs):
    """
    Settings loader for Django.
    """

    name_case = str.upper

    @classmethod
    def get_source(cls) -> Any:
        """
        Return object that has settings set as attributes.
        """
        # type: ignore
        from django.conf import settings  # type: ignore
        return settings  # pragma: no cover
