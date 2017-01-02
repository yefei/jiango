# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

VERSION = "0.6.0"

setup(
    name='jiango',
    version=VERSION,
    url='http://y.minecon.cn',
    author='Feiye',
    author_email='316606233@qq.com',
    description='Django Framework Toolkit.',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires = ['django >=1.4,<1.5'],
)
