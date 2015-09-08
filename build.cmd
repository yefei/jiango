@echo off

del /a/f/q/s *.pyc
python setup.py build_py bdist_egg --exclude-source-files
