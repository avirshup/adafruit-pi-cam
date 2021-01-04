import contextlib
import typing as t
from abc import ABC
import os

import pygame.mouse
import attr

from . import root_logger
from .config import Config

try:
    from .vendor.pitft_touchscreen import pitft_touchscreen as PiTftInput
except ImportError as exc:
    if exc.name != "evdev":
        raise
    PiTftInput = None


T = t.TypeVar("T")

LOGGER = root_logger.getChild("input")


def get_cls(cfg: Config) -> t.Type["InputXface"]:
    if cfg.mouse_driver == "pitft":
        return PigamedrvInput
    else:
        return PygameInput


class InputXface(ABC):
    @classmethod
    def initialize(cls: t.Type[T], cfg: Config) -> T:
        raise NotImplementedError()

    @contextlib.contextmanager
    def cleanup(self):
        raise NotImplementedError()

    def get_click(self) -> t.Optional[t.Tuple[int, int]]:
        raise NotImplementedError()


class PygameInput(InputXface):
    @classmethod
    def initialize(cls: t.Type[T], cfg: Config) -> T:
        os.putenv("SDL_MOUSEDRV", cfg.mouse_driver)
        os.putenv("SDL_MOUSEDEV", str(cfg.mouse_device))
        return cls()

    @contextlib.contextmanager
    def cleanup(self):
        yield  # no cleanup to be done

    def get_click(self) -> t.Optional[t.Tuple[int, int]]:
        for pg_event in pygame.event.get():
            LOGGER.debug(pg_event)
            if pg_event.type is pygame.MOUSEBUTTONDOWN:
                return pygame.mouse.get_pos()


@attr.s(auto_attribs=True)
class PigamedrvInput(InputXface):
    touchscreen: PiTftInput
    last_pos: t.Optional[t.Tuple[int, int]] = None
    is_touched: bool = False

    @classmethod
    def initialize(cls: t.Type[T], cfg: Config) -> T:
        touchscreen = PiTftInput(device_path=str(cfg.mouse_device))
        touchscreen.start()
        return cls(touchscreen)

    @contextlib.contextmanager
    def cleanup(self):
        yield
        self.touchscreen.shutdown(timeout=5)
        if self.touchscreen.thread.is_alive():
            LOGGER.error(
                "input thread failed to terminate; you may need to kill this process"
            )

    def get_click(self) -> t.Optional[t.Tuple[int, int]]:
        """ Register a click at finger's _last_ location
        """
        found_click = None
        for event in self.touchscreen.get_events():
            # LOGGER.debug(event)

            if self.is_touched:
                if event["touch"] == 0:
                    self.is_touched = False
                    found_click = self.last_pos
                    self.last_pos = None
                    LOGGER.debug(f"touch complete: {found_click}")
            else:
                if (
                    event["touch"] == 1
                    and event["x"] is not None
                    and event["y"] is not None
                ):
                    self.last_pos = (event["x"], event["y"])
                    LOGGER.debug(f"touch: {self.last_pos}")
                    self.is_touched = True

        return found_click
