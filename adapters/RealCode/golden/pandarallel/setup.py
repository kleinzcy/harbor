from setuptools import setup, find_packages
import os

# Read version from package
version = {}
with open(os.path.join("pandarallel", "__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

# Read long description from README
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Simple and efficient parallelization tool for pandas"

setup(
    name="pandarallel",
    version=version.get("__version__", "1.0.0"),
    author="Pandarallel Team",
    author_email="example@example.com",
    description="Simple and efficient parallelization tool for pandas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/pandarallel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "psutil>=5.0.0",
        "tqdm>=4.0.0",
        "dill>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    keywords="pandas parallel multiprocessing data-science",
    project_urls={
        "Bug Reports": "https://github.com/example/pandarallel/issues",
        "Source": "https://github.com/example/pandarallel",
    },
)