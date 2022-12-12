"""
Settings collector implementation.
"""

from __future__ import annotations

from typing import Tuple, Optional, Dict, Any, Iterable, Type

from .exceptions import SC_ConfigError, SC_WeirdBugError
from .manager import SC_LoadersManager
from .setting import SC_Setting
from .value import SC_Value, SC_DefaultValue


ScopesKeyType = Optional[Tuple[str, ...]]
ScopesType = Optional[Dict[ScopesKeyType, Type["SettingsCollector"]]]


class _SettingsCollectorMeta(type):
    """
    Metaclass for `SettingsCollector`.
    """

    _default_config_data = {
        # Prefix for settings' names
        "prefix": None,
        # Separator in settings' names.
        "sep": "__",
        # A configurable sequence of loaders to use or skip (see
        # `exclude`).
        "loaders": None,
        # What to do with `loaders`
        # (`False` = use them; `True` = use all others).
        "exclude": True,
        # Load data from all loaders, not just the first successful one.
        "load_all": False,
        # If set to `True`, this loads all settings when the first one is
        # requested. If `False`, they are loaded only when they are requested.
        # This does not affect the automatically reloaded settings.
        "greedy_load": True,
    }

    def __new__(metacls, name, bases, namespace, **kwargs):
        """
        Create and return a new `SettingsCollector` (sub)class.
        """
        class SC_Settings:
            """
            Settings' definitions moved from the main class.
            """

        class SC_Values:
            """
            Actual settings' values.
            """

        class SC_Data:
            """
            Configuration for the current scope.

            This is a separate class to avoid populating `SettingsCollector`
            with too many values and potentially causing a conflict with
            user-defined settings.
            """
            # The name of the current class's scope.
            scope_name: Optional[str] = None
            # Parent scope.
            parent: Optional[Type[SettingsCollector]] = None
            # Root scope
            root: Optional[Type[SettingsCollector]] = None
            # Were settings loaded greedily?
            greedy_loaded: bool = False
            # Children scopes (only valid in the root).
            scopes: ScopesType = dict()

        result = super().__new__(metacls, name, bases, namespace, **kwargs)

        # We want each subclass to have its own `SC_Values` and `SC_Data`.
        result.SC_Settings = SC_Settings  # type: ignore
        result.SC_Values = SC_Values  # type: ignore
        result.SC_Data = SC_Data  # type: ignore

        result.SC_Data.root = result

        result._process_config()
        result._check_bad_names()
        result._expand_defaults()
        result._create_sc_values()

        return result

    def __repr__(cls):
        try:
            result = cls.SC_Data.root.__name__
        except AttributeError:
            result = "<UNKNOWN Settings Collector>"
        if cls.SC_Data.scope_name:
            result += f"({repr(cls.SC_Data.scope_name)})"
        return result

    def _process_config(cls):
        """
        Populate config class with missing defaults, creating it if missing.
        """
        class SC_Config:
            """
            Configuration for the collector.

            All children scopes will share the same one.
            """

        try:
            config = cls.SC_Config
        except AttributeError:
            config = cls.SC_Config = SC_Config

        defined_values = set(dir(config)) - set(dir(object))
        for name, value in cls._default_config_data.items():
            if name not in defined_values:
                setattr(config, name, value)

    def _is_bad_name(cls, name: str) -> bool:
        """
        Return if `name` should not be used as a setting name.
        """
        return (
            # Prefix "SC_" is reserved for Settings Collector's special items.
            name.startswith("SC_")
            # Using the separator can lead to confusing results.
            or name.startswith(cls.SC_Config.sep)
        )

    def _check_bad_names(cls) -> None:
        """
        Raise `SC_ConfigError` if any of configured settings has a bad name.
        """
        bad_names = [
            name
            for name in dir(cls)
            if (
                isinstance(getattr(cls, name), (SC_Setting, SC_Value))
                and cls._is_bad_name(name)
            )
        ]
        if bad_names:
            raise SC_ConfigError(
                f"these settings need to be renamed:"
                f" {', '.join(sorted(bad_names))}",
            )

    def _expand_defaults(cls) -> None:
        """
        Expand simple defaults to normal `SC_Setting` definitions.
        """
        defaults = getattr(cls, "defaults", None)
        if isinstance(defaults, dict):
            delete_defaults = True
            for name, value in defaults.items():
                super().__setattr__(name, SC_Setting(value))
                if name == "defaults":
                    delete_defaults = False
            if delete_defaults:
                delattr(cls, "defaults")

    def _create_sc_values(cls) -> None:
        """
        Populate `SC_Values` subclass with definitions of settings.
        """
        for name in dir(cls):
            sc_setting = getattr(cls, name)
            if not isinstance(sc_setting, SC_Setting):
                continue
            sc_setting.name = name
            sc_value = SC_Value(sc_setting)
            setattr(cls.SC_Settings, name, sc_setting)  # type: ignore
            setattr(cls.SC_Values, name, sc_value)  # type: ignore
            delattr(cls, name)

    def __getattr__(cls, name: str) -> Any:
        """
        Return the `SC_Value` instance for `name`.
        """
        try:
            assert not cls._is_bad_name(name)
            sc_value = getattr(cls.SC_Values, name)  # type: ignore
            assert isinstance(sc_value, SC_Value)
        except (AssertionError, AttributeError):
            raise AttributeError(
                f"type object {repr(cls.__name__)} has no attribute"
                f" {repr(name)}",
            )
        else:
            return sc_value.getter(cls)  # type: ignore

    def __setattr__(cls, name: str, value: Any) -> None:
        """
        Set a new value for a setting.
        """
        try:
            assert not cls._is_bad_name(name)
            sc_value = getattr(cls.SC_Values, name)  # type: ignore
            assert isinstance(sc_value, SC_Value)
        except AssertionError:
            super().__setattr__(name, value)
        except AttributeError:
            raise AttributeError(f"{repr(cls)} has no setting {repr(name)}")
        else:
            sc_value.setter(cls, value)  # type: ignore


class SettingsCollector(metaclass=_SettingsCollectorMeta):
    """
    Settings collector.
    """

    defaults: Dict[str, Any] = dict()

    def __new__(  # type: ignore
        cls,
        scope_name: Optional[str] = None,
    ) -> Type[SettingsCollector]:
        """
        Return a custom scoped instance.
        """
        return cls.get_scope(scope_name)

    @classmethod
    def _get_new(
        cls,
        scope_name: Optional[str] = None,
        parent_scope: Type[SettingsCollector] = None,
    ) -> Type[SettingsCollector]:
        """
        Create and return a custom scoped instance.

        This should normally be in `__new__`, but we want that one for
        convenient use, and this one for actual creation only when needed
        (called by `settings.get_scope`).
        """
        class SettingsCollectorScope(cls):  # type: ignore
            pass

        SettingsCollectorScope._init_child_scope(scope_name, parent_scope)

        return SettingsCollectorScope

    @classmethod
    def _init_child_scope(
        cls,
        scope_name: str,
        parent_scope: Type[SettingsCollector],
    ) -> None:
        """
        Init the current `SettingsCollector` subclass as a child for a scope.
        """
        sc_values = cls.SC_Values  # type: ignore
        sc_data = cls.SC_Data  # type: ignore
        for name, sc_value in parent_scope.get_sc_values():
            setattr(sc_values, name, sc_value.clone())
        root_scope = parent_scope.SC_Data.root  # type: ignore
        sc_data.parent = parent_scope
        sc_data.scope_name = scope_name
        sc_data.root = root_scope
        sc_data.scopes = None
        sc_data.root.SC_Data.scopes[scope_name] = cls  # type: ignore
        cls.SC_Config = parent_scope.SC_Config  # type: ignore
        cls.SC_Settings = parent_scope.SC_Settings  # type: ignore
        cls.__name__ = repr(cls)

    @classmethod
    def get_sc_values(cls) -> Iterable[Tuple[str, SC_Value]]:
        """
        Return a generator of all settings' definitions.

        :return: A generator yielding `(name, sc_value)` tuples, where
            `name` is the string name of each setting and `sc_value` is an
            instance of `SC_Setting` that holds that setting's
            definition.
        """
        sc_values = cls.SC_Values  # type: ignore
        for name in dir(sc_values):
            sc_value = getattr(sc_values, name)
            if isinstance(sc_value, SC_Value):
                yield name, sc_value

    @classmethod
    def get_prefix(cls) -> str:
        """
        Return the correct prefix for settings' names.
        """
        return (
            f"{cls.SC_Config.prefix}{cls.SC_Config.sep}"
            if cls.SC_Config.prefix else
            ""
        )

    @classmethod
    def get_scope_prefix(cls) -> str:
        """
        Return the correct prefix for settings' names including the scope name.
        """
        result = cls.get_prefix()
        scope_name = cls.SC_Data.scope_name  # type: ignore
        if scope_name:
            result = f"{result}{scope_name}{cls.SC_Config.sep}"
        return result

    @classmethod
    def _get_scope(cls, scope_id: ScopesKeyType) -> Type["SettingsCollector"]:
        """
        Return the scope with the given scope ID.

        :param scope_id: A tuple of strings identifying a scope. For example,
            if `cls.SC_Config.sep = "__"` and the scope's name is `"a__bc__d"`,
            the scope ID will be `("a", "bc", "d")`.
        :return: A SettingsCollector class (not instance!) representing the
            requested scope.
        """
        if not scope_id:
            return cls

        sc_data = cls.SC_Data  # type: ignore
        if sc_data.root is None:
            raise SC_WeirdBugError(f"root in {repr(cls)}.SC_Data is None")

        scopes = sc_data.root.SC_Data.scopes  # type: ignore
        if scopes is None:
            raise SC_WeirdBugError(
                f"scopes in {repr(sc_data.root)}.SC_Data is None",
            )

        try:
            result = scopes[scope_id]
        except KeyError:
            result = cls._get_new(
                cls.SC_Config.sep.join(scope_id),
                cls._get_scope(scope_id[:-1]),
            )
            scopes[scope_id] = result
        return result

    @classmethod
    def get_scope(cls, name: Optional[str]) -> Type[SettingsCollector]:
        """
        Return a scope with the given name.
        """
        return cls._get_scope(
            tuple(name.split(cls.SC_Config.sep)) if name else None
        )

    @classmethod
    def get_settings_names(
        cls,
        settings_names: Optional[Iterable[str]] = None,
    ) -> tuple[str, ...]:
        """
        Return a sequence of settings' names.

        :param settings_names: A sequence of names to be returned. If set as
            `None`, all a sequence of all defined settings' names is returned.
        :return: A sequence of settings' names strings.
        """
        return tuple(
            settings_names
            if settings_names else (
                name
                for name in dir(cls.SC_Values)
                if isinstance(getattr(cls.SC_Values, name), SC_Value)
            )
        )

    @classmethod
    def _get_sc_default_values(cls) -> Dict[str, Any]:
        return {name: SC_DefaultValue for name, _ in cls.get_sc_values()}

    @classmethod
    def get_settings(
        cls,
        settings_names: Optional[Iterable[str]] = None,
        expand_names: bool = True,
    ) -> Dict[str, Any]:
        """
        Return settings' values from loaders.

        :param settings_names: Either `None` (meaning "all settings") or an
            iterable of string names of the settings to load.
        :return: A dictionary of loaded values.
        """
        result = dict()
        sc_data = cls.SC_Data  # type: ignore
        greedy_load = (
            cls.SC_Config.greedy_load
            and not sc_data.greedy_loaded
        )
        if greedy_load:
            settings_names = None
            if sc_data.parent is None:
                result.update(cls._get_sc_default_values())
        if expand_names:
            settings_names = cls.get_settings_names(settings_names)
        result.update(SC_LoadersManager.get_settings(cls, settings_names))
        cls._assign_settings_values(result)
        if greedy_load:
            sc_data.greedy_loaded = True
        return result

    @classmethod
    def _assign_settings_values(cls, settings_values: Dict[str, Any]):
        """
        Assign values from a dictionary to `SC_Value` instances.
        """
        for name, value in settings_values.items():
            setattr(cls, name, value)

    @classmethod
    def clear_cache(cls):
        for _, sc_value in cls.get_sc_values():
            sc_value.clear_cache()
        if cls.SC_Data.scopes:
            for scope in cls.SC_Data.scopes.values():
                scope.clear_cache()
