"""Check all function docstrings in a package.
"""
import warnings
import argparse
import importlib
import pkgutil
import inspect
from itertools import chain

from numpydoc.docscrape import NumpyDocString


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('module')
    args = p.parse_args()

    mod = importlib.import_module(args.module)
    for item in sorted(set(all_callables(mod)), key=fullname):
        check_docstring(item)


def check_docstring(f):
    # can't inspect builtins
    if inspect.isbuiltin(f):
        return False

    with warnings.catch_warnings():
        warnings.simplefilter('error')
        try:
            parsed = NumpyDocString(inspect.getdoc(f))
        except:
            print('ERROR PARSING DOCSTRING: %s' % fullname(f))
            print('')
            return False

    if len(parsed['Parameters']) == 0:
        return False

    def iter_docargs():
        for item in chain(parsed['Parameters'], parsed['Other Parameters']):
            for rep in item[0].split(','):
                yield rep.strip()
    doc_args = set(iter_docargs())

    try:
        argspec = inspect.getargspec(f)
    except TypeError as e:
        return False

    # ignore 'self' or 'cls' in the signature for instance methods or
    # class methods.
    args = set(argspec.args)
    args.discard('cls')
    args.discard('self')

    # the docstring might legitimately mention parameters that aren't in
    # the signature if the function takes *args, or **kwargs
    if args != doc_args and len(doc_args) > len(args) and (
            (argspec.varargs is not None) or (argspec.keywords is not None)):
        return False

    # if doc_params != args and len(parsed['Parameters']) > 0:
    if args != doc_args:
        print('%s ( %s )' % (fullname(f), inspect.getfile(f)))

        undoc_args = args.difference(doc_args)
        doc_nonargs = doc_args.difference(args)
        if undoc_args:
            print('  Undocumented arguments:   ', undoc_args)
        if doc_nonargs:
            print('  Documented non-arguments: ', doc_nonargs)
        print()


def all_callables(pkg, root_name=None):
    if root_name is None:
        root_name = pkg.__name__

    def callables_in_module(mod):
        for name, obj in inspect.getmembers(mod):
            if name.startswith('_'):
                continue

            obj_module = inspect.getmodule(obj)
            if obj_module is None:
                continue

            isfunc = (inspect.isclass(obj) or inspect.isfunction(obj) or
                      inspect.isbuiltin(obj))

            if isfunc and inspect.getdoc(obj) is not None and \
                    obj_module.__name__.startswith(root_name):
                yield obj
            if inspect.isclass(obj):
                yield from callables_in_module(obj)

    if inspect.ismodule(pkg):
        yield from callables_in_module(pkg)

    if not hasattr(pkg, '__path__'):
        return

    for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
        if modname.startswith('_'):
            continue
        c = '%s.%s' % (pkg.__name__, modname)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=DeprecationWarning)
                try:
                    mod = importlib.import_module(c)
                except AttributeError:
                    pass

            if ispkg:
                yield from all_callables(mod, root_name)
            yield from callables_in_module(mod)
        except ImportError as e:
            continue


def fullname(f):
    """A long resolved name for a callable, including its module"""
    base = inspect.getmodule(f)
    out = (base.__name__ if base is not None else '') + ':' + f.__name__
    return out


if __name__ == '__main__':
    main()
