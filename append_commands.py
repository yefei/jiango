# -*- coding: utf-8 -*-
# Created on 2015-9-8
# @author: Yefei
import os
import sys
import zipfile


commands = []

for dirpath, dirnames, filenames in os.walk('jiango'):
    p = os.path.split(dirpath)
    if os.path.split(p[0])[1] == 'management' and p[1] == 'commands':
        commands += [os.path.join(dirpath, f) for f in filenames]


if __name__ == '__main__':
    if commands:
        z = zipfile.ZipFile(os.path.join('dist', sys.argv[1]), 'a')
        for p in commands:
            print 'append:', p
            z.write(p, p)
        z.close()
