# Shapes

To install all dependencies simply run `pip install -r requirements.txt`
Target python version is 3.11

For code formatting, run `black .`

This repository uses python dataclasses. These are prefabricated data containers with a couple of usefull
dunder methods already implemented (like `__repr__`, `__eq__`, `__hash__` etc.

Pydantic is a nice library to make sure these dataclasses actually contain the types that are mentioned in 
the dataclass definition.