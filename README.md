# What's this?

This is a Python module which decodes FM-12 (SYNOP) messages into a Python dictionary.

# Example usage

```python
from synack.parser import SYNOPParser

parser = SYNOPParser()
print(parser.parse("AAXX 01004 88889 12782 61506 10094 20047 30111 40197 53007 60001 81541 333 81656 86070"))
```

Or from the command line:

```bash
./cli parse "AAXX 01004 88889 12782 61506 10094 20047 30111 40197 53007 60001 81541 333 81656 86070"
```

# Testing

```bash
PYTHONPATH=$PWD pytest tests/
```
Or

```bash
PYTHONPATH=$PWD python tests/test_generator.py
```

The test generator looks for `.synop`-`.json` pairs and checks the expected output with the actual JSON that was generated.
If the `.json` file doesn't exist, it's created and the test passes vacuously (unless the parser fails to parse the message).

# Architecture

```
synack/
├── builder.py
├── __init__.py
├── manage.py
├── parser.py
├── tables.py
└── tree.py
```

## parser.py

Contains the parser for the messages. Builds the AST and handler errors.

## builder.py

An intermediate layer to handle context, business rules, and build each subset of AST nodes

## tree.py

Contains the definition of each AST node.
The base `ASTNode` class contains support for automatic type conversion (`str -> Any`) with the aid of Python annotations and user-defined `f"convert_{name}"` functions. The conversion functions are called `after` the first conversion is made so if the field type is an index of a table (integer) and the conversion function transforms it into a float, the types of the type annotation and the real value might differ.
Empty ("\") values are saved as `None`. When writing conversion functions, assume any value can be null.

## tables.py

Contains dictionaries with code tables and other mappings.

## manage.py

Contains logic for the CLI.
