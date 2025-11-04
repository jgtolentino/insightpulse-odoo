#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InsightPulse CLI Tool Setup
"""

from setuptools import setup, find_packages

setup(
    name='ipai-cli',
    version='1.0.0',
    description='InsightPulse automation CLI for deployments, testing, and operations',
    author='Jake Tolentino',
    author_email='jgtolentino_rn@yahoo.com',
    url='https://insightpulseai.net',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'requests>=2.28.0',
        'python-dotenv>=0.19.0',
        'psycopg2-binary>=2.9.0',
        'pyyaml>=6.0',
        'tabulate>=0.9.0',
    ],
    entry_points={
        'console_scripts': [
            'ipai=ipai_cli.cli:main',
        ],
    },
    python_requires='>=3.11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
