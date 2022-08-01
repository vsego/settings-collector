"""
SC's equivalent of `NoneType`, used for "not defined" values.
"""


class SCUndefType:
    """
    SC's equivalent of `NoneType`, used for "not defined" values.

    The purpose of this is to allow variables to be "without a value" even when
    `None` can be a legitimate value (so, it cannot be used as a "value not
    set" marker.

    This class is a singleton (i.e., there can only ever be one instance of
    it).
    """

    _instance = None

    def __new__(cls):
        """
        Return instance of `SC_undef`, ensuring that there is always only one.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


SC_undef = SCUndefType()
