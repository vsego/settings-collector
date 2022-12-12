"""
Decorator for populating default argument values from settings collector.
"""

from functools import wraps
import inspect
from typing import Optional, Any, Callable

from .collector import SettingsCollector


def _get_arg(
    settings_collector: Optional[SettingsCollector],
    arg_name: str,
    arg2idx: dict[str, int],
    args: tuple[str, ...],
    kwargs: dict[str, Any],
    default: Any = None,
) -> tuple[Any, Optional[bool]]:
    try:
        # Try to grab assigned value from keyword arguments.
        return kwargs[arg_name], True
    except KeyError:
        try:
            # Try to grab the index of `arg_name` among positional arguments...
            arg_idx = arg2idx[arg_name]
            # ...and check that it indeed has a value.
            return args[arg_idx], False
        except (KeyError, IndexError):
            # If not, apply the default.
            if settings_collector is None:
                return default, None
            else:
                return getattr(settings_collector, arg_name), True


def sc_defaults(
    settings_collector: SettingsCollector,
    *, scope_arg: Optional[str] = None,
) -> Callable:
    """
    Return decorator for populating default values from settings collector.
    """
    def outer(f: Callable) -> Callable:
        @wraps(f)
        def inner(*args, **kwargs):
            f_kwargs = dict()
            args_names = sc_kwargs | set(kwargs)
            if scope_arg is None:
                settings = settings_collector
            else:
                scope, _ = _get_arg(None, scope_arg, arg2idx, args, kwargs)
                settings = settings_collector(scope)
            for arg_name in args_names:
                arg_value, add_to_kwargs = _get_arg(
                    settings, arg_name, arg2idx, args, kwargs,
                )
                if add_to_kwargs:
                    f_kwargs[arg_name] = arg_value
            return f(*args, **f_kwargs)

        # The names of all settings defined in `settings_collector`.
        settings_names = set(settings_collector.get_settings_names())
        # The names of those settings that exist as function's properly named
        # arguments without any defaults (function's defaults override the ones
        # from `settings_collector`, although it's unclear why would you define
        # them in both places).
        sc_kwargs: set[str] = {
            arg_name
            for arg_name, arg_data in inspect.signature(f).parameters.items()
            if (
                # It's one of `settings_collector`'s settings.
                arg_name in settings_names
                # It's a properly named argument (i.e., not `*args`,
                # `**kwargs`, or something similar).
                and any(
                    arg_data.kind == getattr(inspect._ParameterKind, kind)
                    for kind in (
                        "KEYWORD_ONLY", "POSITIONAL_ONLY",
                        "POSITIONAL_OR_KEYWORD",
                    )
                )
                # There is no default value given in the function's signature.
                and arg_data.default is inspect._empty
            )
        }
        # Grab indexes of positional arguments to detect one they are given a
        # value.
        arg2idx = {
            arg_name: idx
            for idx, (arg_name, arg_data) in enumerate(
                inspect.signature(f).parameters.items(),
            )
            if (
                any(
                    arg_data.kind == getattr(inspect._ParameterKind, kind)
                    for kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")
                )
            )
        }
        return inner
    return outer
