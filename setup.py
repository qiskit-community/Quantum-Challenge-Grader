# -*- coding: utf-8 -*-

"""Distutils setup.py."""

from setuptools import setup, find_packages

import codecs
import os.path


# https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='qc_grader',
    version=get_version('qc_grader/__init__.py'),
    description='Grading client for the IBM Quantum Challenge',
    url='https://quantum-computing.ibm.com/',
    author='IBM Quantum Community Team',
    author_email='va@us.ibm.com',
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7',
        "Programming Language :: Python :: 3.8",
        'Topic :: Scientific/Engineering',
    ],
    keywords='qiskit quantum challenge grader',
    packages=find_packages(include=[
        'qc_grader',
        'qc_grader.*'
    ]),
    install_requires=[
        'numpy',
        'qiskit>=0.25',
        'requests',
        'networkx',
        'ipycytoscape',
        'plotly'
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
)
