from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pysondb-v2",
    version="2.0.0",
    author="pysonDB-v2 Developers",
    description="A lightweight JSON database library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/pysondb-v2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "ujson==5.2.0",
        "prettytable==3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest==8.4.1",
            "pytest-mock==3.14.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "pysondb=pysondb.cli:main",
        ],
    },
)