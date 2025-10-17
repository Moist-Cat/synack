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
