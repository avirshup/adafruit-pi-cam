import typing as t
from pathlib import Path

import attr
import pygame

from . import constants
from . import root_logger


LOGGER = root_logger.getChild("ui")

# UI classes ---------------------------------------------------------------

# Small resistive touchscreen is best suited to simple tap interactions.
# Importing a big widget library seemed a bit overkill.  Instead, a couple
# of rudimentary classes are sufficient for the UI elements:


T = t.TypeVar("T")
K = t.TypeVar("K")


@attr.s(frozen=True, auto_attribs=True)
class Icon:
    """
    Icon is a very simple bitmap class, just associates a name and a pygame
    image (PNG loaded from icons directory) for each.
    There isn't a globally-declared fixed list of Icons.  Instead, the list
    is populated at runtime from the contents of the 'icons' directory.
    """

    REGISTRY: t.ClassVar[t.Dict[str, "Icon"]] = {}

    name: str
    bitmap: pygame.Surface

    def __attrs_post_init__(self):
        assert self.name not in self.REGISTRY
        self.REGISTRY[self.name] = self

    @classmethod
    def load(cls: t.Type[K], path: Path) -> K:
        name = path.with_suffix("").name
        bitmap = pygame.image.load(str(path))
        return Icon(name, bitmap)

    @classmethod
    def get(cls: t.Type[T], name: t.Optional[str]) -> t.Optional[T]:
        if not name:
            return None
        elif name in cls.REGISTRY:
            return cls.REGISTRY[name]
        else:
            LOGGER.error(f"No icon named {name}")
            return None


@attr.s(frozen=True, auto_attribs=True)
class Button:
    """
    Button is a simple tappable screen region.  Each has:
     - bounding rect ((X,Y,W,H) in pixels)
     - optional background color and/or Icon (or None), always centered
     - optional foreground Icon, always centered
     - optional single callback function
     - optional single value passed to callback
    Occasionally Buttons are used as a convenience for positioning Icons
    but the taps are ignored.  Stacking order is important; when Buttons
    overlap, lowest/first Button in list takes precedence when processing
    input, and highest/last Button is drawn atop prior Button(s).  This is
    used, for example, to center an Icon by creating a passive Button the
    width of the full screen, but with other buttons left or right that
    may take input precedence (e.g. the Effect labels & buttons).
    """

    name: str
    rect: t.Tuple[int, int, int, int]
    color: t.Optional[str] = None
    icon_bg: t.Optional[Icon] = None
    icon_fg: t.Optional[Icon] = None
    fg_name: t.Optional[str] = None
    bg_name: t.Optional[str] = None
    on_click: t.Optional[constants.Intention] = None
    value: t.Any = None

    @classmethod
    def load(cls: t.Type[K], fg_name: str = None, bg_name: str = None, **kwargs) -> K:
        fg = Icon.get(fg_name)
        bg = Icon.get(bg_name)
        name = kwargs.pop("name", None) or fg_name or bg_name
        return Button(
            name, icon_fg=fg, icon_bg=bg, fg_name=fg_name, bg_name=bg_name, **kwargs
        )

    def selected(self, pos: t.Tuple[int, int]):
        x1 = self.rect[0]
        y1 = self.rect[1]
        x2 = x1 + self.rect[2] - 1
        y2 = y1 + self.rect[3] - 1
        return (x2 >= pos[0] >= x1) and (y2 >= pos[1] >= y1)

    def event(self) -> t.Optional[constants.Event]:
        if self.on_click:
            return constants.Event(self.on_click, self.value)
        else:
            return None
