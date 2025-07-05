from setuptools import setup, find_packages

setup(
    name="factnet",
    version="0.1.0",
    description="A lightweight Python library for building knowledge networks",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "viz": ["matplotlib>=3.5.0", "networkx>=2.8.0"],
    },
    python_requires=">=3.7",
)