from setuptools import setup
setup(
    name='doccheck',
    author='Robert T. McGibbon',
    version='0.1',
    py_modules=['doccheck'],
    entry_points={'console_scripts': ['doccheck = doccheck:main']},
    install_requires=['six', 'numpydoc'],
)
