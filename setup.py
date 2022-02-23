import os
from setuptools import (
    setup,
    find_packages
)

current_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(current_directory, 'README.md'), "r") as readme:
    package_description = readme.read()

setup(
    name="broadkast",
    version="0.1.3",
    author="Zebra.com",
    author_email="sean.corbett@umontana.edu",
    description="REST/GRPC server implementations of Kube App Discovery for service discovery and broadcast of messages/data.",
    long_description=package_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scorbettUM/broadkast",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'idna<2.10',
        'grpcio',
        'grpcio-tools',
        'stringcase',
        'kubernetes',
        'packaging',
        'fastapi[all]',
        'zebra-python-cli',
        'zebra-automate-py-logging',
        'zebra-kube-app-discovery'
    ],
    python_requires='>=3.8'
)
