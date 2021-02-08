# -*- coding: utf-8 -*-

"""Distutils setup.py."""

from setuptools import setup, find_packages

from qc_grader import __version__

setup(
    name='qc_grader',
    version=__version__,
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
        'qiskit>=0.20',
        'requests'
    ],
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
)
