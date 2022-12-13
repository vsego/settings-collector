"""
Exceptions specific for the settings collector.
"""


class SC_Exception(Exception):
    """
    Base exception class for all others to inherit.
    """


class SC_ConfigError(SC_Exception):
    """
    Exception raised when there is a configuration error.
    """


class SC_WeirdBugError(SC_Exception):
    """
    Exception for situations that should not happen in for-mypy-only checks.
    """

    def __init__(self, message):
        super().__init__(
            f"{message} (this shouldn't happen; this check is here only to"
            f" appease mypy",
        )


class SC_NotALoader(SC_Exception):
    """
    Exception raised when something that should be a loader is not one.
    """

    def __init__(self, name):
        super().__init__(f"{name} is not a settings loader")


class SC_SettingsError(SC_Exception):
    """
    Exception raised when `sc_settings` gets broken.
    """
