import contextlib
import functools
import typing as t
import io

import attr
import pygame
from picamera import PiCamera

from .. import constants, config
from .base import Camera

T = t.TypeVar("T")


@functools.lru_cache()
def _buffer(size: t.Tuple[int, int]) -> bytearray:
    return bytearray(size[0] * size[1] * 3)


@attr.s(auto_attribs=True, frozen=True)
class RaspberryPiCamera(Camera):
    camera: "PiCamera"
    preview_resolution: t.Tuple[int, int]
    max_resolution: t.Tuple[int, int]

    @classmethod
    def initialize(cls: t.Type[T], cfg: config.Config) -> T:
        camera = PiCamera(resolution=cfg.screensize)
        return cls(
            camera,
            preview_resolution=cfg.screensize,
            max_resolution=cfg.camera_resolution,
        )

    @contextlib.contextmanager
    def cleanup(self):
        """ Context manager that releases resources on exit
        """
        yield
        self.camera.close()

    def get_preview(self) -> pygame.Surface:
        data = _buffer(self.camera.resolution)
        with io.BytesIO() as stream:
            self.camera.capture(stream, use_video_port=True, format="rgb")
            stream.seek(0)
            stream.readinto(data)

        img = pygame.image.frombuffer(data, self.camera.resolution, "RGB")
        return img

    def write_picture(
        self, stream: t.BinaryIO, settings: config.Settings, fmt: str = "jpeg"
    ):
        # get resolution
        res = self.max_resolution
        if settings.size_mode.value != 1:
            res = (res[0] / settings.size_mode.value, res[1] / settings.size_mode.value)

        try:
            self.camera.resolution = res
            self.camera.capture(
                stream, use_video_port=False, format=fmt, thumbnail=None
            )
        finally:
            self.camera.resolution = self.preview_resolution

    def setup(self, settings: config.Settings):
        self.set_fx_mode(settings.fx_mode)
        self.set_iso_mode(settings.iso_mode)

    def set_fx_mode(self, mode: constants.Fx):
        self.camera.image_effect = [mode.value]
        # buttons[6][5].setBg("fx-" + fxData[fxMode])

    def set_iso_mode(self, iso: constants.IsoSetting):
        self.camera.ISO = iso.iso
        # buttons[7][5].setBg("iso-" + str(isoData[isoMode][0]))
        # buttons[7][7].rect = (isoData[isoMode][1] - 10,) + buttons[7][7].rect[1:]
