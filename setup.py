#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click>=6.0',
    'inotify-simple==1.1.8',
    'transmissionrpc==0.11',
    'PyYAML==5.1.2']

setup_requirements = []


setup(
    author="Laurent Kislaire",
    author_email='teebeenator@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3 :: Only',
    ],
    description="Watch directories for transmission",
    entry_points={
        'console_scripts': [
            'trawa=trawa.cli:main',
        ],
    },
    install_requires=requirements,
    license="ISC license",
    long_description=readme,
    include_package_data=True,
    keywords='transmission watch directory',
    name='trawa',
    packages=find_packages(include=['trawa']),
    setup_requires=setup_requirements,
    url='https://github.com/architek/trawa',
    version='0.5.0',
    zip_safe=False,
)
