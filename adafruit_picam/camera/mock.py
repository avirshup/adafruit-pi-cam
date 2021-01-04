import contextlib
import typing as t
import io
from pathlib import Path
import pkg_resources
import shutil

import attr

from .. import __name__ as pkgname
from .. import config, constants, root_logger

from .base import Camera

T = t.TypeVar("T")

LOGGER = root_logger.getChild("fakecam")


@attr.s(auto_attribs=True)
class MockCamera(Camera):
    img_paths: t.List[Path]
    i_img: int = 0

    @classmethod
    def initialize(cls: t.Type[T], settings: config.Settings) -> T:
        imgdir = Path(pkg_resources.resource_filename(pkgname, "fakephotos"))
        paths = list(imgdir.glob("*.jpg"))
        assert paths
        LOGGER.info("Initialized fake camera")
        return cls(paths)

    @contextlib.contextmanager
    def cleanup(self):
        LOGGER.info("fake camera closed cleanly")

    def get_preview(self) -> io.BytesIO:
        self.i_img += 1
        return self.img_paths[self.i_img % len(self.img_paths)].open("rb")

    def write_picture(self, stream: t.BinaryIO, format):
        with self.img_paths[self.i_img].open("rb") as src:
            shutil.copyfileobj(src, stream)

    def setup(self, settings: config.Settings):
        pass

    def set_fx_mode(self, mode: constants.Fx):
        pass

    def set_iso_mode(self, iso: constants.IsoSetting):
        pass
