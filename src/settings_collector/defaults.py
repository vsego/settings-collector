"""
Decorator for populating default argument values from settings collector.
"""

from functools import wraps
import inspect
from typing import Callable

from .collector import SettingsCollector


def sc_defaults(settings_collector: SettingsCollector) -> Callable:
    """
    Return decorator for populating default values from settings collector.
    """
    def outer(f: Callable) -> Callable:
        @wraps(f)
        def inner(*args, **kwargs):
            f_kwargs = dict()
            args_names = sc_kwargs | set(kwargs)
            for arg_name in args_names:
                try:
                    # Try to grab assigned value from keyword arguments.
                    f_kwargs[arg_name] = kwargs[arg_name]
                except KeyError:
                    try:
                        # Try to grab the index of `arg_name` among positional
                        # arguments...
                        arg_idx = arg2idx[arg_name]
                        # ...and check that it indeed has a value.
                        assert arg_idx < len(args)
                    except (KeyError, AssertionError):
                        # If not, apply the default.
                        f_kwargs[arg_name] = getattr(
                            settings_collector, arg_name,
                        )
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
