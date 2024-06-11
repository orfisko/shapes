from setuptools import setup, find_namespace_packages
import compileall
import os

compile_dir = os.path.join(os.path.dirname(__file__), "dk_geometry")

compileall.compile_dir(compile_dir, force=True)
pyc_files = []
for root, dirs, files in os.walk(compile_dir):
    for file in files:
        if file.endswith(".pyc"):
            pyc_files.append(os.path.relpath(os.path.join(root, file), compile_dir))


setup(
    name="dk_geometry",
    version="0.0.1",
    packages=find_namespace_packages(include=["dk_geometry"]),
    package_data={"dk_geometry": pyc_files},
)
