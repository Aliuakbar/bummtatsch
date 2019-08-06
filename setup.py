from setuptools import setup

setup(
    name="tätscher",
    version="0.0",
    py_modules=["tätscher.py"],
    install_requires=['click'],
    entry_points="""
    [console_scripts]
    bumm=tätscher:bumm
    """
)
