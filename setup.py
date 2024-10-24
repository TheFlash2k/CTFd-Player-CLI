#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='ctfd-cli',
    version='0.1.0',
    packages=find_packages(),
    author='TheFlash2k',
    author_email='root@theflash2k.me',
    include_package_data=True,  # Ensures templates and other non-code files are included
    install_requires=[
        "python-dotenv==1.0.1",
        "Requests==2.32.3",
        "argcomplete",
        "argparse"
    ],
    entry_points={
        'console_scripts': [
            'ctfd=ctfd.ctfd:main',  # This exposes `ctfd.py` as the `ctfd` command
        ],
    },
    package_data={
        '': ['templates/*.sh'],  # Includes template files in the package
    },
)
