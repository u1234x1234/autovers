import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="autovers",
    version="0.0.2",
    author="u1234x1234",
    author_email="u1234x1234@gmail.com",
    description=(""),
    license="MIT",
    keywords="",
    url="https://github.com/u1234x1234/autovers",
    packages=['autovers'],
    install_requires=['appdirs==1.4.3', 'GitPython==2.1.11'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
) 
