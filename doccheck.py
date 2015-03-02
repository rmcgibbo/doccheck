import sys
import types
import warnings
import argparse
import importlib
import pkgutil
import inspect
from itertools import chain

from six import get_function_code, get_function_closure, PY2
from numpydoc.docscrape import NumpyDocString


def main():
    p = argparse.ArgumentParser()
    p.add_argument('module')
    args = p.parse_args()

    mod = importlib.import_module(args.module)
    for item in all_callables(mod):
        m = inspect.getmodule(item)
        if m is not None and m.__name__.startswith(args.module):
            check_docstring(item)


def check_docstring(f):
    if inspect.isbuiltin(f):
        return False

    with warnings.catch_warnings():
        warnings.simplefilter('error')
        try:
            parsed = NumpyDocString(inspect.getdoc(f))
        except ValueError:
            return False

    if len(parsed['Parameters']) == 0:
        return False

    def iter_docargs():
        for item in chain(parsed['Parameters'], parsed['Other Parameters']):
            for rep in item[0].split(','):
                yield rep.strip(': ')
    doc_args = set(iter_docargs())

    try:
        argspec = inspect.getargspec(f)
    except TypeError:
        return False

    args = set(argspec.args)
    args.discard('self')
    args.discard('cls')

    if args != doc_args and len(doc_args) > len(args) and (
            (argspec.varargs is not None) or (argspec.keywords is not None)):
        return False

    # if doc_params != args and len(parsed['Parameters']) > 0:
    if args != doc_args:
        print('ERROR %s.%s' % (inspect.getmodule(f).__name__, f.__name__))
        print('  Signature: ', sorted(args))
        print('  Docs:      ', sorted(doc_args))


def all_callables(pkg):
    def callables_in_module(mod):
        for name, obj in inspect.getmembers(mod):
            if name.startswith('_'):
                continue

            isfunc = (inspect.isclass(obj) or inspect.isfunction(obj) or
                      inspect.isbuiltin(obj))
            if isfunc and inspect.getdoc(obj) is not None:
                yield obj
            if inspect.isclass(obj):
                yield from callables_in_module(obj)

    if inspect.ismodule(pkg):
        yield from callables_in_module(pkg)

    for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
        if modname.startswith('_'):
            continue
        c = '%s.%s' % (pkg.__name__, modname)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=DeprecationWarning)
                mod = importlib.import_module(c)
            if ispkg:
                yield from all_callables(mod)
            yield from callables_in_module(mod)
        except ImportError as e:
            continue


if __name__ == '__main__':
    main()
