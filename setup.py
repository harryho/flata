# coding=utf-8
from setuptools import setup, find_packages
from codecs import open
import os


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    return open(path, encoding='utf-8').read()


setup(
    name="flata",
    version="4.2.0",
    packages=find_packages(),

    # development metadata
    zip_safe=True,

    # metadata for upload to PyPI
    author="Harry Ho",
    author_email="harry.ho_long@yahoo.com",
    description="Flata is inspired by TinyDB and lowdb. It is a tiny, document oriented database optimized for "
                "FlatApi and fun :)",
    license="MIT",
    keywords="database json nosql",
    url="https://github.com/harryho/flata",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent"
    ],

    long_description=read('README.rst'),
)
