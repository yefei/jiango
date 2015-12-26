# -*- coding: utf-8 -*-
import os
from setuptools import setup

VERSION = "0.4.1"

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

# django admin commands 必须要要 py 文件
commands = []

for dirpath, dirnames, filenames in os.walk('jiango'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])
    
    p = os.path.split(dirpath)
    if os.path.split(p[0])[1] == 'management' and p[1] == 'commands':
        commands += [os.path.join(dirpath, f) for f in filenames if f != '__init__.py']


x = setup(
    name = "jiango",
    version = VERSION,
    author = 'Yefei',
    author_email = '316606233@qq.com',
    url = 'http://djangobbs.com',
    install_requires = ['django >=1.4,<1.5'],
    package_data = {'':['*.*']},
    packages = packages,
    data_files = data_files
)

print "=" * 32
print 

if commands:
    import zipfile
    for c,v,f in x.dist_files:
        z = zipfile.ZipFile(f, 'a')
        for p in commands:
            print 'append:', p
            z.write(p, p)
        z.close()
