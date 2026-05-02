from setuptools import setup, find_packages

setup(
    name="pygame-core",
    version="0.1.1",
    description="Shared pygame utilities for personal game projects",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Umutcan Ekinci",
    author_email="umutcannekinci@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests*", ".venv*"]),
    install_requires=[
        "pygame-ce",
        "pyyaml",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.14",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries",
    ],
)