"""
Class for getting, setting, and holding the actual settings' values.
"""

from __future__ import annotations

from typing import Any, Optional, Type, TYPE_CHECKING

from .exceptions import SC_ConfigError
from .setting import SC_Setting
from .undef import SC_undef


if TYPE_CHECKING:
    from .collector import SettingsCollector  # pragma: no cover


class SC_DefaultValue:
    """
    Internal class used to represent default value without setting it.
    """


class SC_Value:
    """
    A class for holding actual values for settings.
    """

    def __init__(self, sc_setting: SC_Setting):
        self.sc_setting = sc_setting
        self.value_is_set = False
        self.value = None

    def clone(self) -> SC_Value:
        """
        Return `SC_Value` configured for the same `SC_Setting`.
        """
        return type(self)(self.sc_setting)

    def _get_default_value(self) -> Any:
        """
        Return default value if defined or raise a `ValueError` exception.
        """
        result = self.sc_setting.default
        if result is SC_undef:
            raise ValueError(
                f"setting {repr(self.sc_setting.name)} must be defined",
            )
        else:
            return result

    def cast(self, value: Optional[Any]) -> Any:
        """
        Return `value` with proper type casting.

        :param value: Value to cast as `self.value_type`.
        :raise ValueError: Raised if the casting fails and
            `self.default_on_error` is not `True`.
        :return: Value cast to the given type.
        """
        if value == SC_DefaultValue:
            return self._get_default_value()
        if self.sc_setting.value_type is None:
            return value

        has_correct_type = isinstance(value, self.sc_setting.value_type)

        if has_correct_type:
            return value
        else:
            try:
                return self.sc_setting.value_type(value)
            except Exception as ex:
                if self.sc_setting.default_on_error:
                    return self._get_default_value()
                else:
                    raise TypeError(
                        "invalid value {value} for setting {setting_name}"
                        " (it should be of type {type_name})".format(
                            value=repr(value),
                            setting_name=self.sc_setting.name,
                            type_name=self.sc_setting.value_type.__name__,
                        ),
                    ) from ex

    def getter(self, settings_collector: Type[SettingsCollector]) -> Any:
        """
        Return the value for the setting ((re)loaded if needed).
        """
        if self.sc_setting.name is None:
            # This should never happen
            raise SC_ConfigError(  # pragma: no cover
                "there be bug: setting not assigned its name",
            )

        if not self.sc_setting.no_cache and self.value_is_set:
            # Not a reloadble setting and we already had the value cached, so
            # we can just return it.
            return self.value

        # Get the value.
        parent_collector = settings_collector.SC_Data.parent  # type: ignore
        values = settings_collector.get_settings([self.sc_setting.name])

        # Return it or fall back to parent.
        try:
            self.value = self.cast(values[self.sc_setting.name])
        except KeyError:
            if parent_collector:
                sc_value = getattr(
                    parent_collector.SC_Values, self.sc_setting.name,
                )
                return sc_value.getter(parent_collector)
            else:
                return self._get_default_value()
        else:
            self.value_is_set = True
            return self.value

    def setter(
        self, settings_collector: Type[SettingsCollector], value: Any,
    ) -> None:
        """
        Set the value for the setting unless it's an auto-reloading one.
        """
        self.value = self.cast(value)
        if not self.sc_setting.no_cache:
            self.value_is_set = True

    def clear_cache(self) -> None:
        """
        Invalidate any cache that this value might hold.
        """
        self.value = None
        self.value_is_set = False
