import contextlib
import time
import typing as t
from collections import deque

import pygame
import attr
from sortedcontainers import SortedList

from . import constants, camera, root_logger
from .storage import Storage
from .config import Config, Settings

if t.TYPE_CHECKING:
    from .camera import Camera

T = t.TypeVar("T")

LOGGER = root_logger.getChild("state")


@attr.s(auto_attribs=True)
class State:
    """ The (singleton) state object stores all mutable state of the program

    The state is mutated via event handlers in the `event_handlers` module.
    """

    cfg: Config
    settings: Settings

    # interfaces
    camera: "Camera"
    storage: Storage

    # lifecycle state
    frame_times: deque
    shutdown: bool = False
    took_picture: bool = False

    # operating state
    screen_mode: constants.ScreenMode = constants.ScreenMode.viewfinder
    last_screen_mode: constants.ScreenMode = None
    setting_idx: int = 0

    # image storage state
    image_ids: SortedList = attr.ib(factory=SortedList)
    """ All known stored image ids """

    selected_image_index: int = None
    """ The index of the selected image in the image_ids list"""

    last_image: t.Optional[pygame.Surface] = None
    last_image_id: t.Optional[int] = None

    @contextlib.contextmanager
    def cleanup(self):
        """ Context manager that releases resources on exit
        """
        with self.camera.cleanup():
            yield
            self.storage.save_settings(self.settings)

    @classmethod
    def initialize(cls: t.Type[T], cfg: Config) -> T:
        storage = Storage.initialize(cfg)
        settings = storage.load_settings()
        cam = camera.get_cls(fake=cfg.mock_camera).initialize(cfg)
        image_indexes = storage.get_stored_ids()
        state = cls(
            camera=cam,
            cfg=cfg,
            settings=settings,
            storage=storage,
            frame_times=deque(maxlen=cfg.fps_window),
            image_ids=SortedList(image_indexes),
            selected_image_index=0 if image_indexes else None,
        )
        return state

    def get_display_image(self) -> t.Optional[pygame.Surface]:
        """ Returns this image to draw - either the camera output or the loaded image
        """
        if self.took_picture or self.screen_mode in (
            constants.ScreenMode.image_viewer,
            constants.ScreenMode.confirm_delete,
        ):
            return self.load_image()
        else:
            img = self.camera.get_preview()
            self.last_image = img
            self.last_image_id = None
            return img

    def load_image(self) -> pygame.Surface:
        """ Return the currently selected image, loading it first if necessary
        """
        selected_id = self.image_ids[self.selected_image_index]
        if not self.last_image or (self.last_image_id != selected_id):
            self.last_image = self.storage.load_image(selected_id)
            self.last_image_id = selected_id
        return self.last_image

    def fps_tick(self) -> float:
        """ To be called once each frame.

        Returns:
             float: current FPS averaged over last 10 frames
        """
        tm = time.time()
        self.frame_times.append(tm)
        try:
            return (len(self.frame_times) - 1) / (tm - self.frame_times[0])
        except ZeroDivisionError:
            return 0
        except Exception as exc:
            LOGGER.error("fps calc error", exc_info=True)
