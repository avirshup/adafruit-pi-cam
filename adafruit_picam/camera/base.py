import contextlib
import typing as t
from abc import ABC

import pygame

from .. import config, constants

T = t.TypeVar("T")


class Camera(ABC):
    @classmethod
    def initialize(cls: t.Type[T], settings: config.Settings) -> T:
        raise NotImplementedError()

    @contextlib.contextmanager
    def cleanup(self):
        raise NotImplementedError()

    def get_preview(self) -> pygame.Surface:
        raise NotImplementedError()

    def write_picture(
        self, stream: t.BinaryIO, settings: config.Settings,
    ):
        raise NotImplementedError()

    def setup(self, settings: config.Settings):
        raise NotImplementedError()

    def set_fx_mode(self, mode: constants.Fx):
        raise NotImplementedError()

    def set_iso_mode(self, iso: constants.IsoSetting):
        raise NotImplementedError()
