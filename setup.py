#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
import pypandoc

with open('README.rst') as readme_file:
    readme = pypandoc.convert_text(readme_file.read(), to='md', format='rst')

requirements = [
    'keyname',
    'matplotlib',
    'python-slugify',
    'distutils-strtobool',
    'typing-extensions',
]

setup_requirements = ['pytest-runner', 'pypandoc-binary']

test_requirements = ['pytest>=3', ]

setup(
    author="Matthew Andres Moreno",
    author_email='m.more500@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description="teeplot automatically saves a copy of rendered Jupyter notebook plots",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='teeplot',
    name='teeplot',
    packages=find_packages(include=['teeplot', 'teeplot.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mmore500/teeplot',
    version='1.4.1',
    zip_safe=False,
)
