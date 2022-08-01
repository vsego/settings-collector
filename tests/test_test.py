import io
import textwrap
import unittest
import unittest.mock

from settings_collector import SCTest, sc_test_print_expected, sc_test_run

from tests.utils import TestsBase, patch_env


class TestTest(TestsBase):

    def tearDown(self):
        SCTest.clear_cache()
        super().tearDown()

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_print(self, mock_stdout):
        sc_test_print_expected()
        self.assertEqual(
            mock_stdout.getvalue(),
            textwrap.dedent(
                """\
                SCTest__JustAString = 'covfefe'
                SCTest__AnInteger = 17
                SCTest__scope1__scope2__JustAString = 'covfefe, but scoped'
                SCTest__scope1__scope2__AnInteger = 1719
                """,
            ),
        )

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_run(self, mock_stdout):
        with patch_env(
            SCTest__JustAString="covfefe",
            SCTest__AnInteger=17,
            SCTest__scope1__scope2__JustAString="covfefe, but scoped",
            SCTest__scope1__scope2__AnInteger=1719,
        ):
            sc_test_run(False)
        self.assertEqual(
            mock_stdout.getvalue(),
            "Success: all tests have passed.\n",
        )

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_run_verbose(self, mock_stdout):
        with patch_env(
            SCTest__JustAString="covfefe",
            SCTest__AnInteger=17,
            SCTest__scope1__scope2__JustAString="covfefe, but scoped",
            SCTest__scope1__scope2__AnInteger=1719,
        ):
            sc_test_run(True)
        self.assertEqual(
            mock_stdout.getvalue(),
            textwrap.dedent(
                """\
                Test for 'JustAString' passed using SC_EnvironLoader.
                Test for 'AnInteger' passed using SC_EnvironLoader.
                Test for 'scope1__scope2__JustAString' passed using SC_EnvironLoader.
                Test for 'scope1__scope2__AnInteger' passed using SC_EnvironLoader.
                """,  # noqa: E501
            ),
        )

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_run_verbose_missing(self, mock_stdout):
        with patch_env(
            SCTest__JustAString="covfefe",
            SCTest__scope1__scope2__JustAString="covfefe, but scoped",
        ):
            sc_test_run(True)
        self.assertEqual(
            mock_stdout.getvalue(),
            textwrap.dedent(
                """\
                Test for 'JustAString' passed using SC_EnvironLoader.
                Error getting value for SCTest__AnInteger loaded from SC_EnvironLoader: setting 'AnInteger' must be defined
                Test for 'scope1__scope2__JustAString' passed using SC_EnvironLoader.
                Error getting value for SCTest__scope1__scope2__AnInteger loaded from SC_EnvironLoader: setting 'AnInteger' must be defined
                """,  # noqa: E501
            ),
        )

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_run_verbose_bad_cast(self, mock_stdout):
        self.maxDiff = None
        with patch_env(
            SCTest__JustAString="covfefe",
            SCTest__AnInteger="seventeen",
            SCTest__scope1__scope2__JustAString="covfefe, but scoped",
            SCTest__scope1__scope2__AnInteger="seventeen-nineteen",
        ):
            sc_test_run(True)
        self.assertEqual(
            mock_stdout.getvalue(),
            textwrap.dedent(
                """\
                Test for 'JustAString' passed using SC_EnvironLoader.
                Error casting value for SCTest__AnInteger loaded from SC_EnvironLoader: invalid value 'seventeen' for setting AnInteger (it should be of type int)
                Test for 'scope1__scope2__JustAString' passed using SC_EnvironLoader.
                Error casting value for SCTest__scope1__scope2__AnInteger loaded from SC_EnvironLoader: invalid value 'seventeen-nineteen' for setting AnInteger (it should be of type int)
                """,  # noqa: E501
            ),
        )

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_run_verbose_bad_value(self, mock_stdout):
        self.maxDiff = None
        with patch_env(
            SCTest__JustAString="covfefe",
            SCTest__AnInteger=19,
            SCTest__scope1__scope2__JustAString="covfefe, but scoped",
            SCTest__scope1__scope2__AnInteger=1917,
        ):
            sc_test_run(True)
        self.assertEqual(
            mock_stdout.getvalue(),
            textwrap.dedent(
                """\
                Test for 'JustAString' passed using SC_EnvironLoader.
                Invalid value received for SCTest__AnInteger loaded from SC_EnvironLoader: 19 != 17
                Test for 'scope1__scope2__JustAString' passed using SC_EnvironLoader.
                Invalid value received for SCTest__scope1__scope2__AnInteger loaded from SC_EnvironLoader: 1917 != 1719
                """,  # noqa: E501
            ),
        )
