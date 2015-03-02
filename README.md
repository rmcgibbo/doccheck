# doccheck
*Check that all docstrings satisfy Numpy format*

This is a small script that goes through functions, methods and classes in a package and looks for
inconsistencies between the signatures and (Numpy format) docstring.

In particular, it's on the lookout for undocumented arguments, or documented arguments which don't actually
appear in the function signature.

### Examples
```
$ doccheck scipy.linalg

[ ... snip ...]

scipy.linalg.matfuncs:expm ( /Users/rmcgibbo/projects/scipy/scipy/linalg/matfuncs.py )
  Undocumented arguments:    {'q'}
``` 

```
doccheck numpy.ma.extras
numpy.ma.extras:compress_rowcols ( /Users/rmcgibbo/miniconda/envs/scipy/lib/python3.4/site-packages/numpy/ma/extras.py )
  Undocumented arguments:    {'x'}

numpy.ma.extras:flatnotmasked_edges ( /Users/rmcgibbo/miniconda/envs/scipy/lib/python3.4/site-packages/numpy/ma/extras.py )
  Undocumented arguments:    {'a'}
  Documented non-arguments:  {'arr'}

numpy.ma.extras:vander ( /Users/rmcgibbo/miniconda/envs/scipy/lib/python3.4/site-packages/numpy/ma/extras.py )
  Undocumented arguments:    {'n'}
  Documented non-arguments:  {'N', 'increasing'}
```

### Installation
```
$ pip install https://github.com/rmcgibbo/doccheck/archive/master.zip
```

### Dependencies
- python3.3 or later
- [numpydoc](https://github.com/numpy/numpydoc)

