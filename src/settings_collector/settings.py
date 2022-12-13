"""
Settings for a loader that does not require any frameworks.
"""


class SC_Settings(dict):
    """
    Settings for a loader that does not require any frameworks.

    This class is a singleton (i.e., there can only ever be one instance of
    it).
    """

    _instance = None

    def __new__(cls):
        """
        Return instance of `SC_Settings`, ensuring that there is only one.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


sc_settings = SC_Settings()
