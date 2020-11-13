#!/usr/bin/env python3
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
