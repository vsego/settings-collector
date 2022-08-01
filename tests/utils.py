"""
Testing utilities.
"""

from contextlib import contextmanager
import os
import unittest
from unittest.mock import patch

from settings_collector import SC_EnvironLoader


# This loader was made mostly for testing, so we need to enable it.
SC_EnvironLoader.enabled = True


class TestsBase(unittest.TestCase):
    """
    The base unit tests class, used as a foundation for all other unit tests.
    """

    def setUp(self):
        """
        For future uses (common resets between runs).
        """
        pass

    def tearDown(self):
        """
        For future uses (common resets between runs).
        """
        pass


@contextmanager
def patch_env(_upper: bool = True, **kwargs):
    """
    Patch `os.environ` with `kwargs` (nothing else left in there!).

    :param _upper: If set to `True`, all the names from `kwargs` are changed to
        uppercase. This is normal for environment variables, but we do have one
        test where we want it turned off, hence having this argument.
    """
    kwargs = {
        name.upper() if _upper else name: str(value)
        for name, value in kwargs.items()
    }
    with patch.dict(os.environ, kwargs, clear=True):
        yield
