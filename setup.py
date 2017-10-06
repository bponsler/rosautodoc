#!/usr/bin/env python
from distutils.core import setup


setup(
    name='rosautodoc',
    version='1.0',
    description='Automatically generate documentation for ROS nodes',
    author='Brett Ponsler',
    author_email='ponsler@gmail.com',
    url='https://github.com/bponsler/rosautodoc',
    packages=['rosautodoc'],
    scripts=['scripts/rosautodoc']
)
