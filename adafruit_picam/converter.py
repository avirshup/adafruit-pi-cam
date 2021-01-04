import typing as t
import io
import functools

import attr
import yuv2rgb

import pygame

T = t.TypeVar("T")


@attr.s(frozen=True, auto_attribs=True)
class ImageConverter:
    size: t.Tuple[int, int]
    pixels: int
    rgb: bytearray
    yuv: bytearray

    @functools.lru_cache()
    @classmethod
    def create(cls: t.Type[T], size: t.Tuple[int, int]) -> T:
        pixels = size[0] * size[1]
        rgb = bytearray(3 * pixels)
        yuv = bytearray((3 * pixels) // 2)
        return cls(size, pixels, rgb, yuv)

    def convert_stream(self, stream: io.BytesIO) -> pygame.Surface:
        stream.seek(0)
        stream.readinto(self.yuv)
        yuv2rgb.convert(self.yuv, self.rgb, self.size[0], self.size[1])
        img = pygame.image.frombuffer(self.rgb[0 : 3 * self.pixels], self.size, "RGB")
        return img
