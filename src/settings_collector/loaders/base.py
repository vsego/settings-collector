"""
Base class for settings loading classes.
"""

from typing import Iterable, Any, Optional, Type, Callable

from ..exceptions import SC_ConfigError


class _SC_LoaderBaseMeta(type):
    """
    Metaclass for `SC_LoaderBase` used to auto-register each class.
    """

    def __new__(metacls, name, bases, namespace, **kwargs):
        # Create the class.
        result = super().__new__(metacls, name, bases, namespace, **kwargs)

        # Register that class.
        from ..manager import SC_LoadersManager
        SC_LoadersManager.register_loader(result)

        # Return the new class as one normally would in `__new__`.
        return result


class SC_LoaderBase(metaclass=_SC_LoaderBaseMeta):
    """
    Base class for settings loading classes.
    """

    # A tuple of exceptions that are not errors but indicate that there are no
    # settings available for this loader.
    no_settings_exceptions: tuple[Type[Exception], ...] = (ImportError,)

    # Higher number, higher priority (i.e., its values override those from the
    # lower priority loaders). Makes sense when `load_all` is `True`.
    # Set this to a negative number for low-priority sources (see
    # `env.SC_EnvironLoader` class) and to a positive number if you
    # want to ensure that some source is preferred. Most loaders should
    # probably stick to the default 0.
    priority: int = 0

    # Should this loader be used by default?
    # This was mostly added to disable `SC_EnvironLoader` by default while
    # still being able to enable it for testing purposes.
    enabled: bool = True

    # The case used for names of the settings in the given loader's framework.
    # This is a function that takes and returns a string.
    # For example, Django loader will use `str.upper` because configuration
    # values in Django are traditionally defined as upper-case strings.
    name_case: Optional[Callable[[str], str]] = None

    @classmethod
    def _get_source_name(cls, name: str) -> str:
        """
        Return the name of the setting `name` in the framework's config.
        """
        if cls.name_case is None:
            return name
        elif callable(cls.name_case):
            return cls.name_case(name)
        else:
            raise SC_ConfigError(
                f"name_case must be a callable, not a {type(cls.name_case)}",
            )

    @classmethod
    def get_settings(
        cls, prefix: str, settings_names: Iterable[str],
    ) -> Optional[dict[str, Any]]:
        """
        Return the relevant settings values in a dictionary.

        You probably don't want to override this, as it only calls
        `load_settings` and ignores the exceptions that are meant to happen if
        the settings does not exist.

        :param prefix: A prefix to be added to each name. For example, is some
            setting's name is `"bar"` and the prefix is `"foo_"` it is loaded
            from `"foo_bar"` and saved as `"bar"`.
        :param settings_names: A list of string names to of the variables to
            load.
        :return: The relevant settings values in a dictionary or `None` if it's
            failing.
        """
        if not cls.enabled:
            return None

        if not isinstance(settings_names, list):
            settings_names = list(settings_names)

        prefix = cls._get_source_name(prefix)

        try:
            result, success = cls.load_settings(prefix, settings_names)
        except Exception as e:
            if isinstance(e, cls. no_settings_exceptions):
                return None
            else:
                raise
        else:
            return result if success else None

    @classmethod
    def load_settings(
        cls, prefix: str, settings_names: list[str],
    ) -> tuple[dict[str, Any], bool]:
        """
        Return the relevant settings values in a dictionary.

        This is what you want to override in subclasses for specific settings.

        :param prefix: A prefix to be added to each name. For example, is some
            setting's name is `"bar"` and the prefix is `"foo_"` it is loaded
            from `"foo_bar"` and saved as `"bar"`.
        :param settings_names: A list of string names to of the variables to
            load.
        :raise NotImplementedError: This method needs to be overriden in
            subclasses, with the override raising some exceptions from
            `no_settings_exceptions` tuple in case the settings doesn't exist.
            If needed, redefine that tuple in your subclass to contain all the
            relevant exception classes.
        :return: A tuple containing
            1. relevant settings values in a dictionary, and
            2. a Boolean describing the success of the loading.
        """
        raise NotImplementedError(
            f"do not use {cls.__name__} directly (use a class that inherits it"
            f" and has `load_settings` properly defined)",
        )  # pragma: no cover


class SC_LoaderFromAttribs(SC_LoaderBase):
    """
    Base for settings loader classes that load settings as attributes.
    """

    @classmethod
    def get_source(cls):
        """
        Return object that has settings set as attributes.
        """
        raise NotImplementedError(
            f"do not use {cls.__name__} directly (use a class that inherits it"
            f" and has `get_source` properly defined)",
        )  # pragma: no cover

    @classmethod
    def load_settings(
        cls, prefix: str, settings_names: list[str],
    ) -> tuple[dict[str, Any], bool]:
        """
        Return the relevant settings values in a dictionary.

        This is what you want to override in subclasses for specific settingss.

        :param prefix: A prefix to be added to each name. For example, is some
            setting's name is `"bar"` and the prefix is `"foo_"` it is loaded
            from `"foo_bar"` and saved as `"bar"`.
        :param settings_names: A list of string names to of the variables to
            load.
        :raise NotImplementedError: This method needs to be overriden in
            subclasses, with the override raising some exceptions from
            `no_settings_exceptions` tuple in case the settings doesn't exist.
            If needed, redefine that tuple in your subclass to contain all the
            relevant exception classes.
        :return: A tuple containing
            1. relevant settings values in a dictionary, and
            2. a Boolean describing the success of the loading.
        """
        source = cls.get_source()
        result = dict()
        for name in settings_names:
            try:
                source_name = cls._get_source_name(name)
                result[name] = getattr(source, f"{prefix}{source_name}")
            except AttributeError:
                pass
        return result, True  # Always `True`; failures happen with imports


class SC_LoaderFromDict(SC_LoaderBase):
    """
    Base for settings loader classes that load settings from dictionaries.
    """

    @classmethod
    def get_source(cls):
        """
        Return dictionary that with settings.
        """
        raise NotImplementedError(
            f"do not use {cls.__name__} directly (use a class that inherits it"
            f" and has `get_source` properly defined)",
        )  # pragma: no cover

    @classmethod
    def load_settings(
        cls, prefix: str, settings_names: list[str],
    ) -> tuple[dict[str, Any], bool]:
        """
        Return the relevant settings values in a dictionary.

        This is what you want to override in subclasses for specific settingss.

        :param prefix: A prefix to be added to each name. For example, is some
            setting's name is `"bar"` and the prefix is `"foo_"` it is loaded
            from `"foo_bar"` and saved as `"bar"`.
        :param settings_names: A list of string names to of the variables to
            load.
        :raise NotImplementedError: This method needs to be overriden in
            subclasses, with the override raising some exceptions from
            `no_settings_exceptions` tuple in case the settings doesn't exist.
            If needed, redefine that tuple in your subclass to contain all the
            relevant exception classes.
        :return: A tuple containing
            1. relevant settings values in a dictionary; and
            2. a Boolean describing the success of the loading (success here
               means that at least one value was found and loaded).
        """
        source = cls.get_source()
        result = dict()
        for name in settings_names:
            try:
                source_name = cls._get_source_name(name)
                result[name] = source[f"{prefix}{source_name}"]
            except KeyError:
                pass
        return result, bool(result)
