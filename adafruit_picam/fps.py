import typing as t
import attr


@attr.s(frozen=True, auto_attribs=True)
class FpsCounter:
    window: int
    buffer: deque
