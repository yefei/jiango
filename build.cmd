@echo off

rem python setup.py bdist_wheel

del /a/f/q/s *.pyc
set PATH=D:\Python27;D:\Python27\Scripts
python setup.py build_py bdist_egg --exclude-source-files
python append_commands.py jiango-0.2.0-py2.7.egg

del /a/f/q/s *.pyc
set PATH=D:\Apps\Python26;D:\Apps\Python26\Scripts
python setup.py build_py bdist_egg --exclude-source-files
python append_commands.py jiango-0.2.0-py2.6.egg
