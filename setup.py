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


with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()


with open('requirements-qiskit.txt') as f:
    QISKIT_REQUIREMENTS = f.read().splitlines()


with open('requirements-jupyter.txt') as f:
    JUPYTER_REQUIREMENTS = f.read().splitlines()


setup(
    name='qc_grader',
    version=get_version('qc_grader/__init__.py'),
    description='Grading client for the IBM Quantum Challenge',
    url='https://quantum.ibm.com/',
    author='IBM Quantum Community Team',
    author_email='va@us.ibm.com',
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering',
    ],
    keywords='qiskit quantum challenge grader',
    packages=find_packages(include=[
        'qc_grader',
        'qc_grader.*',
        'qc_grader_json',
        'qc_grader_json.*',
    ]),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    extras_require={
        'qiskit': QISKIT_REQUIREMENTS,
        'jupyter': JUPYTER_REQUIREMENTS
    },
)
