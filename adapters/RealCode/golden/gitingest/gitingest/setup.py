#!/usr/bin/env python3
"""
Setup script for GitIngest package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitingest",
    version="1.0.0",
    author="GitIngest Team",
    author_email="team@gitingest.dev",
    description="Automated Code Repository Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gitingest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "tomli>=2.0.1; python_version < '3.11'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "web": [
            "flask>=2.0",
            "flask-cors>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gitingest=gitingest.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)