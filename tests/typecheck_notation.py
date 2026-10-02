"""Static checks run with mypy --strict, including unused-ignore detection."""

from typing import TYPE_CHECKING, Any, Dict

from notation import Notation


if TYPE_CHECKING:
    initial: Dict[str, int] = {"timeout": 30}
    notes = Notation(initial)

    @notes("public", method="GET")
    def greet(name: str, *, repeat: int = 1) -> str:
        return name * repeat

    message: str = greet("Ada", repeat=2)
    greet(42)  # type: ignore[arg-type]
    greet("Ada", unknown=True)  # type: ignore[call-arg]
    wrong_result: int = greet("Ada")  # type: ignore[assignment]
    Notation([])  # type: ignore[arg-type]
    notes(self="x")(greet)

    metadata: Any = notes[greet]
    timeout: Any = notes.timeout
    registered: bool = greet in notes
    present: bool = "timeout" in notes
    populated: bool = bool(notes)
    notes.retries = 2
    notes["retries"] = 3
    del notes.retries
    notes[[]]  # type: ignore[index]
    notes[[]] = 1  # type: ignore[index]
    [] in notes  # type: ignore[attr-defined]
