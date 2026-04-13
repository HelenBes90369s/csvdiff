"""Package setup for csvdiff."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="csvdiff",
    version="0.1.0",
    description="A fast CLI tool for diffing two CSV files with configurable key columns and output formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="csvdiff contributors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*"]),
    entry_points={
        "console_scripts": [
            "csvdiff=csvdiff.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ]
    },
)
