"""
Testing functions for Settings Collector.
"""

from typing import Tuple, Any

from settings_collector import SC_LoadersManager
from settings_collector import SettingsCollector, SC_Setting


TV_KeysType = str | Tuple[tuple[str, ...], str]
TV_ValuesType = dict[str, Any]
TV_Type = dict[TV_KeysType, TV_ValuesType]
TEST_VALUES: TV_Type = {
    "JustAString": {"kwargs": dict(), "value": "covfefe"},
    "AnInteger": {"kwargs": dict(value_type=int), "value": 17},
    (("scope1", "scope2"), "JustAString"): {"value": "covfefe, but scoped"},
    (("scope1", "scope2"), "AnInteger"): {"value": 1719},
}


SCTest = type(
    "SCTest",
    (SettingsCollector,),
    {
        "SC_Config": type("SC_Config", (object,), {"prefix": "SCTest"}),
        **{
            tv_name: SC_Setting(  # type: ignore
                default_on_error=False, **tv_def["kwargs"],
            )
            for tv_name, tv_def in TEST_VALUES.items()
            if isinstance(tv_name, str)
        }
    },
)


class _TestItem:
    """
    Auxiliary class for analysing test values.
    """

    def __init__(self, test_name: TV_KeysType) -> None:
        sep = SCTest.SC_Config.sep  # type: ignore
        prefix = SCTest.SC_Config.prefix  # type: ignore
        scopes_path: tuple[str, ...]
        if isinstance(test_name, tuple):
            self.settings = SCTest(sep.join(test_name[0]))
            self.name = test_name[1]
            scopes_path = (*test_name[0], test_name[1])
        elif isinstance(test_name, str):
            self.settings = SCTest
            self.name = test_name
            scopes_path = (test_name,)
        else:
            raise ValueError(  # pragma: no cover
                f"invalid type for {repr(test_name)}; must be a string or"
                f" a tuple of strings",
            )
        self.test_name_str = sep.join(scopes_path)
        self.source_name = f"{prefix}{sep}{self.test_name_str}"


def sc_test_print_expected():
    """
    Print expected values to use in the framework's config.
    """
    for test_name, test_def in TEST_VALUES.items():
        test_item = _TestItem(test_name)
        print(f"{test_item.source_name} = {repr(test_def['value'])}")


def sc_test_run(verbose: bool = True):
    """
    Run tests for Settings Collector and print the results.

    :param verbose: If set to `True`, a report is printed for each test.
        Otherwise, only failed test are printed or a message that all have
        passed if none fail.
    """
    def last_loader_name() -> str:
        last_loader = SC_LoadersManager.last_successful_loader
        if last_loader:
            return last_loader.__name__
        else:
            # If we ever get here, it's a bug.
            return "<NO LOADER>"  # pragma: no cover

    def msg() -> str:
        # This needs to be called after the `getattr` line below, so it cannot
        # be a simple string variable prepared before the `try...except` block.
        return f"for {test_item.source_name} loaded from {last_loader_name()}"

    report: list[str] = list()
    for test_name, test_def in TEST_VALUES.items():
        test_item = _TestItem(test_name)
        try:
            settings_value = getattr(test_item.settings, test_item.name)
            assert settings_value == test_def["value"]
        except ValueError as e:
            report.append(f"Error getting value {msg()}: {e}")
        except TypeError as e:
            report.append(f"Error casting value {msg()}: {e}")
        except AssertionError:
            report.append(
                f"Invalid value received {msg()}:"
                f" {repr(settings_value)} != {repr(test_def['value'])}",
            )
        except Exception as e:  # pragma: no cover
            # It shouldn't be possible to end up here.
            report.append(f"Unexpected error {msg()}: {e}")
        else:
            if verbose:
                report.append(
                    f"Test for {repr(test_item.test_name_str)} passed using"
                    f" {last_loader_name()}.",
                )

    if not report:
        report = ["Success: all tests have passed."]

    print("\n".join(report))
