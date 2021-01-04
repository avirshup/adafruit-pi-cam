import typing as _t

from .base import Camera

from .mock import MockCamera

try:
    from .pi import RaspberryPiCamera
except ImportError as exc:
    assert exc.name == "picamera"
    _rpi_exc = exc
    RaspberryPiCamera = None
else:
    _rpi_exc = None


def get_cls(fake: bool = False) -> _t.Type[Camera]:
    if fake:
        return MockCamera
    elif _rpi_exc is not None:
        raise _rpi_exc
    else:
        return RaspberryPiCamera
