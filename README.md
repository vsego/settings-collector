# `settings-collector`: Settings collector class for Python

This Python 3.6+ package is meant to be used by other packages (i.e., not
directly by final projects). Its purpose is to collect settings defined in
various frameworks, so you don't have to make special implementations for
those.

A typical use case would be to define something like this:

```python
from settings_collector import SettingsCollector, SC_Setting

class my_settings(SettingsCollector):
    foo = SC_Setting("bar")
```

and then use `my_settings.foo` in your code. The value of `foo` would come from
Django's `settings` if your package is used in a Django app, from Flask's app
config if it's used in a Flask project, etc.

# Content

1. [Supported frameworks](#supported-frameworks)
2. [How to use](#how-to-use)
3. [Settings definitions](#settings-definitions)
4. [Prefix](#prefix)
5. [Name cases](#name-cases)
6. [Scopes](#scopes)
7. [Fine tuning](#fine-tuning)
8. [Custom loaders](#custom-loaders)
9. [Testing custom loaders](#testing-custom-loaders)

## Supported frameworks

Currently, Settings Collector supports [Bottle](https://bottlepy.org/docs/dev/),
[CherryPy](https://cherrypy.dev/), [Django](http://www.djangoproject.com/),
[Flask](https://flask.palletsprojects.com/),
[Pyramid](https://trypyramid.com/), and [TurboGears](https://turbogears.org/).
Please note that the support for most of those was written just by reading
their docs. I am experienced only with Django and Flask.

Each framework is handled by its loader class. These are located in the
`settings_collector.loader` package. Apart from the loaders for specific
frameworks, there is also a loader for environment variables, called
`SC_EnvironLoader`.

Settings for frameworks are not normally loaded directly from the environment,
but they come from some sort of config file (which might import some of them
from the environment), so `SC_EnvironLoader` is disabled by default. To enable
it, one can run

```python
from settings_collector import SC_EnvironLoader

SC_EnvironLoader.enabled = True
```

## How to use

The most general way to use this is to define a class similar to the models in
ORM frameworks:

```python
from settings_collector import SettingsCollector, SC_Setting

class my_settings(SettingsCollector):
    foo = SC_Setting("bar")
```

After this, just use `my_settings.foo`, which will fetch value `foo` from your
project's configuration (which can be standard Django, Flask, etc). If the
value is not defined, it will be set to the default value (`"bar"`, in this
example).

Note that the loaders adjust character cases as needed. This means that your
`my_settings.foo` will come from `django.conf.settings.FOO` if your packages is
used in a Django app, but from `cherrypy.config["foo"]` or
`cherrypy.request.app.config["foo"]` if it's used in a CherryPy project. For
details, see [Name cases](#name-cases).

If one needs to define only the default values for the settings, without
further adjustments, this can be used as well:

```python
from settings_collector import SettingsCollector

class my_settings(SettingsCollector):
    defaults = {"bar": "foo"}
```

This example is equivalent to the previous one, but it doesn't allow
adjustments described in the next section.

## Settings definitions

The constructor of `SC_Setting` accepts the following arguments (presented here
with their default values):

* `default_value` [optional]: The default value to be returned if it's not
  defined in settings. If neither this nor the setting's value in the
  framework's config is set, a `ValueError` exception is raised.

* `no_cache=False` [optional, keyword only]: If `True`, skip cashing. This
  means that the actual value of the setting is fetched every time it is
  requested. Normally, the settings are set up when the app runs and they do
  not change, so caching is usually the best way to go.

* `value_type=None` [optional, keyword only]: A type to convert the value to
  (for example, `int`). This can be used to ensure the correct type of the
  value, even if the settings provide something else (for example, a string, as
  is normal for `os.environ`).

* `default_on_error=True` [optional, keyword only]: This affects the behaviour
  when the value of a setting is set, but the casting to the given `value_type`
  fails. If set to `True`, the returned value is `default_value` (a
  `ValueError` exception is raised if that value is not set). However, if this
  is set to `False`, requesting the value not defined in the app will result in
  `TypeError` exception, regardless of `default_value`.

## Prefix

If you want your config settings to be distinguished from all others (those
used by other packages or the framework itself), you can define a prefix:

```python
from settings_collector import SettingsCollector, SC_Setting

class my_settings(SettingsCollector):
    class SC_Config:
        prefix = "test"
    foo = SC_Setting("bar")
```

Now, the value of `my_settings.foo` will come from `test__foo` in the
framework's config.

## Name cases

Each loader (the class responsible for the actual loading of the settings'
values from the frameworks' configs) can define the case for the names. For
example, Django keeps settings in variables that have upper-case names, so the
corresponding loader will change your names to upper-case as will the one for
`os.environ`, but not the one for TurboGears.

So, in the previous example, the value of `my_settings.foo` will come from
`TEST__FOO` if the running framework is Django, but it'll come from `test__foo`
if your package is used in a TurboGears app.

## Scopes

Settings can get their values relative to scopes, not unlike names given to
loggers. The default separator for scopes' names is double underscore (`"__"`).

Let us take a look at the following Django example. Let's say that the settings
are defined as follows (in some framework that uses upper-case names):
```python
FOO = "bar"
SC1__SC2__FOO = "bard"
```

We then define our settings collector:
```python
from settings_collector import SettingsCollector, SC_Setting

class my_settings(SettingsCollector):
    foo = SC_Setting("bar")
```

The values obtained will be as follows:

* `my_settings.foo == "bar"` is defined in the settings as `FOO=bar`;
* `my_settings("sc1").foo == "bar"` is inherited from the root scope because
  there is no `foo` defined in the scope `"sc1"` (i.e., there is no
  `SC1__FOO`);
* `my_settings("sc1__sc2").foo == "bard"` is directly defined in the settings
  as `SC1__SC2__FOO = "bard"`;
* `my_settings("sc1__sc2__sc3").foo == "bard"` is again inherited from the
  parent scope `"sc1__sc2"` because there is no `SC1__SC2__SC3__FOO`
  definition.

## Fine tuning

Each subclass of `SettingsCollector` can have a class `SC_Config` in its
definition, which has a similar role to `Meta` in Django's models: it defines
various properties that define the settings collector's behaviour. The
available attributes are as follows:

* `prefix` [default: `None`]: Explained [here](#prefix).

* `sep` [default: `"__"`]: A string containing a separator used between prefix,
  scopes, and settings' names.

* `loaders` [default: `None`]: A sequence of loaders' names, defining the
  loaders that should be skipped or used (see `exclude` property). This list
  can contain loaders that are unknown to the Settings Collector, making it
  possible to explicitly include or exclude loaders that might be defined only
  in some frameworks (i.e., outside of `settings_collector`).

* `exclude` [default: `True`]: If `True`, the loaders listed in `loaders` are
  skipped; otherwise, they are the only ones used. Note that the loaders with
  `enabled` set to `False` will always be skipped.

* `load_all` [default: `False`]: If `False`, the settings are loaded by the
  first loader that can provide them (i.e., the other loaders are not used). If
  this is changed to `True`, the values are fetched from all the loaders, with
  the latter ones overriding the former ones. This'll rarely make sense, since
  each loader covers one framework and a project is not likely to use more than
  one of them, but it might make sense if you want to combine settings in the
  environment variables with those in the framework.

* `greedy_load` [default: `True`]: If `True`, then all the settings are loaded
  when one of them is requested, thus minimising the overhead of the settings
  collector. If this is changed to `False`, each setting is loaded when
  requested and not before.

## Custom loaders

Adding the support for Settings Collector to your own framework is easy.
Obviously, you can submit it to me for inclusion in this package, but it is
just as easy to include it in the package itself.

All you need to do is create a module:
```python
try:
    from settings_collector import SC_LoaderBase
except ImportError:
    pass
else:
    class SC_MyFrameworkLoader(SC_LoaderBase):
        ...
```

The name of your loader class must begin with `SC_` and end with `Loader`.

Make sure that this module is imported. The creation of a subclass of
`SC_LoaderBase` automatically registers it with the one that Settings Collector
can recognise.

Notice that this module does not require `settings_collector`, so your
framework won't require it either. If no packages requiring
`settings_collector` are used, the import above will be silently ignored.

Since the configurations are usually defined as attributes in modules or
classes (like in Django) or as keys in a dictionary (like in Flask or
`os.environ`), there are subclasses that make it easier to implement loaders
for any framework using one of these approaches. These are
`SC_LoaderFromAttribs` and `SC_LoaderFromDict`. To see how they are used, see
the source code for
[`SC_DjangoLoader`](https://github.com/vsego/settings-collector/blob/master/src/settings_collector/loaders/django.py) and for
[`SC_EnvironLoader`](https://github.com/vsego/settings-collector/blob/master/src/settings_collector/loaders/env.py).

## Testing custom loaders

One can easily test their shiny new loader.

1. Install Settings Collector in some project using your framework:
   ```bash
   pip install settings_collector
   ```

2. Add your loader to the project and import its module (so that the loader
   gets registered).

3. Run the following code:
   ```python
   import settings_collector
   settings_collector.sc_test_print_expected()
   ```
   This will print the testing variables as the test function expects them.

4. Add these settings to your project's config. Make sure that they are named
   consistently with how it is done in your framework. For example, the names
   of these settings would be uppercased in Django's config, despite them
   having mixed cases in the output of `sc_test_print_expected`.

5. Restart your project and run:
   ```python
    import settings_collector
    settings_collector.sc_test_run()
    ```

Note that you can also run `settings_collector.sc_test_run(False)` if you want
a bit less verbose output.
