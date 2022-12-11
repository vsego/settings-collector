"""
Class that defines an individual setting to be collected.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Optional, Dict, Type, Any

from .undef import SC_undef


class SC_Setting:
    """
    Class that defines an individual setting to be collected.

    You can compare this to Django's `django.db.models.Field`.
    """

    def __init__(
        self,
        default: Any = SC_undef,
        *,
        no_cache: bool = False,
        value_type: Optional[Type[Any]] = None,
        default_on_error: bool = True,
    ) -> None:
        """
        Initialise class instance.

        :param default: Default value for the setting.
        :param no_cache: If `True`, the value of this setting is never
            saved. Instead, it is reloaded from settings every time it is
            requested.
        :param value_type: If not `None`, this is used as a callable for the
            returned value. For example, if set to `int`, the value returned
            will be `int(value_fetched_from_settings)`.
        :param default_on_error: Fall back to `default` when casting fails due
            to invalid data.
        """
        self.default = default
        self.no_cache = no_cache
        self.value_type = value_type
        self.default_on_error = default_on_error
        self.name: Optional[str] = None

    def __copy__(self) -> SC_Setting:
        return type(self)(
            default=self.default,
            no_cache=self.no_cache,
            value_type=self.value_type,
            default_on_error=self.default_on_error,
        )

    def __deepcopy__(self, memo: Dict[int, Any]) -> SC_Setting:
        id_self = id(self)
        try:
            return memo[id_self]
        except KeyError:
            result = memo[id_self] = type(self)(
                default=deepcopy(self.default),
                no_cache=deepcopy(self.no_cache),
                value_type=deepcopy(self.value_type),
                default_on_error=deepcopy(self.default_on_error),
            )
            return result
