"""
A class to register and manage all loaders.
"""

from __future__ import annotations

from typing import Type, Optional, Iterable, Dict, Any, TYPE_CHECKING

from .exceptions import SC_ConfigError, SC_NotALoader

if TYPE_CHECKING:  # pragma: no cover
    from .collector import SettingsCollector
    from .loaders.base import SC_LoaderBase


class SC_LoadersManager:
    """
    A class to register and manage all loaders.
    """

    loader_name_prefix: str = "SC_"
    loader_name_suffix: str = "Loader"
    _loaders: Dict[str, Type[SC_LoaderBase]] = dict()
    last_successful_loader: Optional[Type[SC_LoaderBase]] = None

    @classmethod
    def is_loader(cls, class_: Type[SC_LoaderBase]):
        """
        Return `True` is `class_` is a loader.
        """
        class_name = class_.__name__
        if (
            class_name.startswith(cls.loader_name_prefix)
            and class_name.endswith(cls.loader_name_suffix)
        ):
            from .loaders.base import SC_LoaderBase
            return issubclass(class_, SC_LoaderBase)
        else:
            return False

    @classmethod
    def get_loader_name(cls, class_: Type[SC_LoaderBase]):
        """
        Return loader name or raise `SC_NotALoader` exception if not a loader.
        """
        class_name = class_.__name__
        if cls.is_loader(class_):
            if cls.loader_name_prefix:
                class_name = class_name[len(cls.loader_name_prefix):]
            if cls.loader_name_suffix:
                class_name = class_name[:-len(cls.loader_name_suffix)]
            return class_name
        else:
            raise SC_NotALoader(class_name)

    @classmethod
    def register_loader(cls, loader_class: Type[SC_LoaderBase]) -> None:
        """
        Register loader defined by the given class.
        """
        try:
            loader_name = cls.get_loader_name(loader_class)
        except SC_NotALoader:
            pass
        else:
            cls._loaders[loader_name] = loader_class

    @classmethod
    def _get_loaders(
        cls,
        settings_collector: Type[SettingsCollector],
        *,
        reverse=False,
    ) -> Iterable[Type[Any]]:
        """
        Return a generator of settings loader classes.

        For arguments, see :py:meth:`get_settings`.

        :param settings_collector: A `SettingsCollector` (sub)class for which
            the settings are being loaded).
        :param reverse: Return loader classes sorted in reverse order (by
            descending priority).
        """
        if (
            settings_collector.SC_Config.exclude
            or settings_collector.SC_Config.loaders
        ):
            # Find out which loaders are needed and then `yield` only those.
            include_loaders = (
                set(settings_collector.SC_Config.loaders)
                if settings_collector.SC_Config.loaders
                else set()
            )
            if settings_collector.SC_Config.exclude:
                include_loaders = set(cls._loaders) - include_loaders
            else:
                unknown_loaders = include_loaders - set(cls._loaders)
                if unknown_loaders and not include_loaders - unknown_loaders:
                    raise SC_ConfigError(
                        f"attempting to use only unknown loaders:"
                        f" {', '.join(sorted(unknown_loaders))}",
                    )
            for loader_name, loader_class in sorted(
                cls._loaders.items(),
                key=lambda it: it[1].priority,
                reverse=reverse,
            ):
                if loader_class.enabled and loader_name in include_loaders:
                    yield loader_class
        else:
            # So, you want to use only listed loaders, but then you're not
            # listing any of them? Brilliant! :-P
            raise ValueError(
                '''"You're not making any sense at all."'''
                ''' -- Captain Jack Sparrow'''
            )

    @classmethod
    def get_settings(
        cls,
        settings_collector: Type[SettingsCollector],
        settings_names: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """
        Load and return settings values as a dictionary.

        :param settings_collector: A `SettingsCollector` (sub)class for which
            the settings are being loaded.
        :param settings_names: Either `None` (meaning "all settings") or an
            iterable of string names of the settings to load).
        :raise SC_ConfigError: Raised when attempting to use only unknown
            loaders (i.e., none of the `loaders` exist and `settings.exclude`
            is set to `False`). The logic here is that you may settings.exclude
            whatever loaders you want (even those not defined, because some
            other project might have them outside of this package), but if you
            include only those loaders not available (in this package or in the
            project using it), then the whole thing becomes useless, and that's
            likely an error in the configuration of the settings collector.
        :return: A dictionary associating settings' names with their values.
        """
        result = dict()
        prefix = settings_collector.get_scope_prefix()
        load_all = settings_collector.SC_Config.load_all
        for settings_loader in cls._get_loaders(
            settings_collector, reverse=not load_all,
        ):
            settings_values = settings_loader.get_settings(
                prefix, settings_names,
            )
            if settings_values is not None:
                cls.last_successful_loader = settings_loader
                if load_all:
                    result.update(settings_values)
                else:
                    return settings_values
        return result
