# SPDX-FileCopyrightText: 2026-present Adam Patterson <adpatter2000@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Hashable
from typing import Any, Callable, Dict, Optional, TypeVar


_F = TypeVar("_F", bound=Callable[..., Any])


class Notation:
    """A dictionary-backed metadata registry and function decorator.

    The supplied dictionary becomes the instance namespace, so string keys
    are readable and writable as attributes and ``vars(notation)`` is the
    dictionary itself.
    """

    # Widen the key type so functions can be stored alongside string keys.
    __dict__: Dict[Any, Any]

    def __init__(self, /, annotation: Optional[Dict[Any, Any]] = None) -> None:
        # Assigning a non-dictionary raises TypeError natively.
        self.__dict__ = {} if annotation is None else annotation

    # Only reached when normal attribute lookup fails. Present so that
    # ``mypy --strict`` accepts arbitrary attribute reads.
    def __getattr__(self, key: str) -> Any:
        raise AttributeError(key)

    # Present so that ``mypy --strict`` accepts arbitrary attribute writes.
    def __setattr__(self, key: str, value: Any) -> None:
        object.__setattr__(self, key, value)

    def __getitem__(self, key: Hashable) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self.__dict__[key] = value

    def __contains__(self, key: Hashable) -> bool:
        return key in self.__dict__

    def __bool__(self) -> bool:
        return bool(self.__dict__)

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(annotation={self.__dict__})"

    def __call__(self, /, *args: Any, **kwargs: Any) -> Callable[[_F], _F]:
        def decorator(fn: _F) -> _F:
            self.__dict__[fn] = dict(enumerate(args), **kwargs)
            return fn

        return decorator
