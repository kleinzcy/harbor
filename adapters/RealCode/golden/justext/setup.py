from setuptools import setup, find_packages

setup(
    name="justext",
    version="1.0.0",
    description="Web content extraction library for multilingual web pages",
    author="jusText Team",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "chardet>=4.0.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)