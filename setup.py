from setuptools import setup, find_namespace_packages

setup(
    name="dk_geometry",
    version="0.0.1",
    packages=find_namespace_packages(exclude=["tests"]),
)
