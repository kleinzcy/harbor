from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tsfresh",
    version="0.1.0",
    author="tsfresh Developers",
    description="Time Series Feature Extraction Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blue-yonder/tsfresh",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "scipy>=1.4.0",
        "scikit-learn>=0.22.0",
        "statsmodels>=0.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=20.8b1",
            "flake8>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tsfresh-extract-features=tsfresh.cli.extract_features:main",
        ],
    },
)