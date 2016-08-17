# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

VERSION = "0.4.4"

setup(
    name='jiango',
    version=VERSION,
    url='http://djangobbs.com',
    author='Yefei',
    author_email='316606233@qq.com',
    description=('A high-level Python Web framework that encourages '
                 'rapid development and clean, pragmatic design.'),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires = ['django >=1.4,<1.5'],
)
