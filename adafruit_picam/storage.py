import contextlib
import io
import stat
import typing as t
from pathlib import Path
import attr

import pygame

from . import root_logger, config, util

if t.TYPE_CHECKING:
    from .state import State

T = t.TypeVar("T")
K = t.TypeVar("K")

LOGGER = root_logger.getChild("io")

PHOTO_DIR = Path("Photos")


@attr.s(auto_attribs=True, frozen=True)
class Storage:
    settings_path: Path
    photo_dir: Path
    image_ids: t.Dict[int, bool] = attr.ib(factory=dict)

    @classmethod
    def initialize(cls: t.Type[T], cfg: config.Config) -> T:
        storage = Storage(
            settings_path=cfg.settings_cache, photo_dir=cfg.photo_storage_dir
        )
        return storage

    def imgpath(self, idx: int) -> Path:
        return self.photo_dir / f"IMG_{idx:04d}.JPG"

    def increment_idx(self, current: int, inc: int) -> int:
        raise NotImplementedError()

    def save_settings(self, settings: config.Settings):
        # util.dump_json(settings, self.settings_path)
        pass

    def load_settings(self) -> config.Settings:
        return config.Settings()
        # if not self.settings_path.is_file():
        #     LOGGER.info("no settings file found; using defaults")
        #     return config.Settings()
        # else:
        #     settings = util.load_json(config.Settings, self.settings_path)
        #     return settings

    def get_stored_ids(self) -> t.List[int]:
        """ A list of all image idxes in the storage folder
        """
        indexes = []
        for f in self.photo_dir.glob("IMG_*.JPG"):
            try:
                idx = int(f.name[4:-4])
            except TypeError:
                LOGGER.warning(f'Failed to extract index from "{f.name}"')
            else:
                indexes.append(idx)
        return indexes

    def load_image(self, imgid: int) -> pygame.Surface:
        path = self.imgpath(imgid)
        img = pygame.image.load(str(path))
        return img

    @contextlib.contextmanager
    def write_image(self, imgid: int) -> t.BinaryIO:
        path = self.imgpath(imgid)
        with path.open("wb") as stream:
            yield stream
        path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

    def delete_image(self, imgid: int):
        path = self.imgpath(imgid)
        path.unlink()
        self.image_ids[imgid] = False
