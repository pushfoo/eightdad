"""
This is a hacky stub that makes tests work. Why? Not yet sure. ¯\\_(ツ)_/¯
A python discord user suggested this fix, and didn't elaborate.

In the past, tests ran fine with util.py being auto-imported from the
tests dir.

When I upgraded pytest or one of the other libraries (pip, setuptools, ?)
to get current arcade versions to work, it appears to have changed how
import works. Adding this file to turn tests into a module works even if
I'm not exactly sure why.

"""
