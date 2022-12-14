from settings_collector import SettingsCollector, SC_Setting, sc_defaults

from tests.utils import TestsBase, patch_env


class my_settings(SettingsCollector):

    foo = SC_Setting("food")
    bar = SC_Setting("bard")


class TestBasicFunctionality(TestsBase):

    def tearDown(self):
        my_settings.clear_cache()

    def test_defaults(self):

        @sc_defaults(my_settings)
        def f(x, foo):
            return f"{x}:{foo}"

        self.assertEqual(f(17), "17:food")
        self.assertEqual(f(17, "afoot"), "17:afoot")
        self.assertEqual(f(17, foo="afoot"), "17:afoot")
        self.assertEqual(f(x=17, foo="afoot"), "17:afoot")

        self.assertEqual(f(17), "17:food")
        self.assertEqual(f(x=17), "17:food")
        self.assertEqual(f(17, foo="afoot"), "17:afoot")

    def test_defaults_with_func_defaults(self):

        @sc_defaults(my_settings)
        def f(x, y=17, foo="toe-foo"):
            return f"{x}:{y}:{foo}"

        self.assertEqual(f(13, 19), "13:19:toe-foo")
        self.assertEqual(f(13, 19, "afoot"), "13:19:afoot")
        self.assertEqual(f(13, 19, foo="afoot"), "13:19:afoot")
        self.assertEqual(f(13, y=19, foo="afoot"), "13:19:afoot")

        self.assertEqual(f(13), "13:17:toe-foo")
        self.assertEqual(f(x=13), "13:17:toe-foo")
        self.assertEqual(f(13, foo="afoot"), "13:17:afoot")

    def test_defaults_on_method(self):

        class Foo:

            @sc_defaults(my_settings)
            def f(self, x, foo):
                return f"{x}:{foo}"

        self.assertEqual(Foo().f(17), "17:food")
        self.assertEqual(Foo().f(17, "afoot"), "17:afoot")
        self.assertEqual(Foo().f(17, foo="afoot"), "17:afoot")
        self.assertEqual(Foo().f(x=17, foo="afoot"), "17:afoot")

        self.assertEqual(Foo().f(17), "17:food")
        self.assertEqual(Foo().f(x=17), "17:food")
        self.assertEqual(Foo().f(17, foo="afoot"), "17:afoot")

    def test_defaults_on_classmethod(self):

        class Foo:

            @classmethod
            @sc_defaults(my_settings)
            def f(cls, x, foo):
                return f"{x}:{foo}"

        self.assertEqual(Foo.f(17), "17:food")
        self.assertEqual(Foo.f(17, "afoot"), "17:afoot")
        self.assertEqual(Foo.f(17, foo="afoot"), "17:afoot")
        self.assertEqual(Foo.f(x=17, foo="afoot"), "17:afoot")

        self.assertEqual(Foo.f(17), "17:food")
        self.assertEqual(Foo.f(x=17), "17:food")
        self.assertEqual(Foo.f(17, foo="afoot"), "17:afoot")

    def test_defaults_on_staticmethod(self):

        class Foo:

            @staticmethod
            @sc_defaults(my_settings)
            def f(x, foo):
                return f"{x}:{foo}"

        self.assertEqual(Foo.f(17), "17:food")
        self.assertEqual(Foo.f(17, "afoot"), "17:afoot")
        self.assertEqual(Foo.f(17, foo="afoot"), "17:afoot")
        self.assertEqual(Foo.f(x=17, foo="afoot"), "17:afoot")

        self.assertEqual(Foo.f(17), "17:food")
        self.assertEqual(Foo.f(x=17), "17:food")
        self.assertEqual(Foo.f(17, foo="afoot"), "17:afoot")

    def test_defaults_on_init(self):

        class Foo:

            @sc_defaults(my_settings)
            def __init__(self, x, foo):
                self.x = x
                self.foo = foo

            def f(self):
                return f"{self.x}:{self.foo}"

        self.assertEqual(Foo(17).f(), "17:food")
        self.assertEqual(Foo(17, "afoot").f(), "17:afoot")
        self.assertEqual(Foo(17, foo="afoot").f(), "17:afoot")
        self.assertEqual(Foo(x=17, foo="afoot").f(), "17:afoot")

        self.assertEqual(Foo(17).f(), "17:food")
        self.assertEqual(Foo(x=17).f(), "17:food")
        self.assertEqual(Foo(17, foo="afoot").f(), "17:afoot")

    def test_defaults_with_scope(self):

        @sc_defaults(my_settings, scope_arg="scope")
        def f(x, foo, scope=""):
            return f"{x}:{foo}"

        with patch_env(foo="fool", scoped__foo="toe-foo"):
            self.assertEqual(f(17), "17:fool")
            self.assertEqual(f(17, "afoot"), "17:afoot")
            self.assertEqual(f(17, scope="scoped"), "17:toe-foo")
            self.assertEqual(f(17, "afoot", "scoped"), "17:afoot")
