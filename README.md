# Notation

Declare metadata beside a function with a decorator and retrieve it later from a registry.

## Installation

```bash
python -m pip install notation
```

Requires Python 3.8 or newer.

## Usage

**Annotate functions**

Positional values are stored under integer keys starting at `0`; keyword values are stored under their names. The decorator returns the original function unchanged.

```python
from notation import Notation

notes = Notation()

@notes("public", method="GET")
def index():
    return "Hello, World!"

notes[index]   # {0: 'public', 'method': 'GET'}
```

**Enumerate registered functions**

The supplied dictionary becomes the instance namespace, so `vars()` returns it directly:

```python
routes = Notation()

@routes(path="/hello")
def hello():
    return "Hello, World!"

handlers = {meta["path"]: fn for fn, meta in vars(routes).items()}
```

**Annotate methods**

Inside a class body the decorator receives the plain function, so metadata is stored under that function. Accessing a method through an instance returns a new bound-method object each time, so look up the function itself:

```python
class Service:
    @notes(route="/items")
    def items(self):
        return []

    @classmethod
    @notes(route="/create")
    def create(cls):
        return cls()

service = Service()

notes[Service.items]            # {'route': '/items'}
notes[service.items.__func__]   # {'route': '/items'}
notes[Service.create.__func__]  # {'route': '/create'}
```

Each stored function carries a `__qualname__` such as `"Service.items"` that identifies its class when enumerating.

## API

### The Notation class

**Notation(annotation=None)**

- `annotation` A `dict` or `None`, as the instance's `__dict__`. A supplied dictionary is used directly, not copied, and `vars(notation)` returns it. `None` creates a new empty dictionary.

#### Usage notes

- `notation[key]`, `notation[key] = value`, `key in notation` operate on the backing dictionary.
- `notation.name` reads, writes, or deletes the string key `"name"`. A missing attribute raises `AttributeError`; a missing item raises `KeyError`.
- `bool(notation)` is `False` when the backing dictionary is empty.
- `notation(*args, **kwargs)` returns a decorator that stores `{0: args[0], ..., **kwargs}` under the decorated function and returns the function. Decorating the same function again replaces its metadata.

Because the dictionary is the instance namespace, keys that spell Python protocol hooks, such as `__deepcopy__` or `__getstate__`, are visible to `copy` and `pickle`; avoid them as metadata keys. Overrides on `dict` subclasses, such as `defaultdict.__missing__`, apply to item access but not to attribute access. Iteration, `len`, `get`, item deletion, and equality are not provided; use `vars(notation)` instead.

Metadata is keyed by the exact function object. If another decorator replaces the function, the registry still refers to whichever object it was given. Decorators apply bottom-up, so apply `Notation` outermost to key the metadata by the object your module name refers to:

```python
import functools

@notes("public", method="GET")
@functools.lru_cache
def index():
    return "Hello, World!"

notes[index]   # {0: 'public', 'method': 'GET'}
```

With the order reversed, `notes` stores metadata under the inner function and `lru_cache` binds `index` to a new wrapper, so `notes[index]` raises `KeyError`.

`classmethod` and `staticmethod` are the exception. Apply `Notation` beneath them, directly on the function. Applied above, it stores metadata under the `classmethod` or `staticmethod` wrapper object, which attribute access never returns, and the metadata is reachable only through the class `__dict__`.

## Tests

```bash
python -m pip install -e . mypy
python -m unittest discover -s tests
python -m mypy --strict src/notation tests/typecheck_notation.py
```

## License

MIT. See [LICENSE](https://github.com/adamjpatterson/notation/blob/main/LICENSE).
