import contextlib
import typing as t
import pkg_resources
from pathlib import Path
import os

import attr
import pygame, pygame.font

from . import __name__ as pkgname, root_logger
from . import constants
from . import elements
from . import init_buttons
from . import input_device

if t.TYPE_CHECKING:
    from .config import Config


T = t.TypeVar("T")

LOGGER = root_logger.getChild("app")
ICON_PATH = Path(pkg_resources.resource_filename(pkgname, "icons"))
GRAY = (128, 128, 128)
FPS_OFFSET = (2, 2)
FPS_FONT = "Helvetica"
FPS_FONTSIZE = 8


@attr.s(frozen=True, auto_attribs=True)
class UI:
    size: t.Tuple[int, int]
    icons: t.Dict[str, elements.Icon]
    buttons: t.Dict[constants.ScreenMode, t.List[elements.Button]]
    screen: pygame.Surface
    font: pygame.font.Font
    input_dev: input_device.InputXface

    @classmethod
    def initialize(cls: t.Type[T], cfg: "Config") -> T:
        """ Create UI elements and initialize pygame screen
        """

        # load UI elements
        icons = {}
        for path in ICON_PATH.glob("*.png"):
            icon = elements.Icon.load(path)
            icons[icon.name] = icon
        buttons = init_buttons.init_buttons()

        # initialize input device
        input_dev_cls = input_device.get_cls(cfg)
        input_dev = input_dev_cls.initialize(cfg)

        # initialize screen
        os.putenv("SDL_VIDEODRIVER", cfg.video_driver)
        os.putenv("SDL_FBDEV", str(cfg.video_device))
        pygame.init()
        pygame.display.init()
        pygame.mouse.set_visible(False)
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        font = pygame.font.SysFont(FPS_FONT, FPS_FONTSIZE)

        ui = cls(cfg.screensize, icons, buttons, screen, font, input_dev=input_dev)
        return ui

    @contextlib.contextmanager
    def cleanup(self):
        """ Context manager that releases resources on exit
        """
        yield
        pygame.quit()

    def redraw(
        self,
        img: t.Optional[pygame.Surface],
        mode: t.Optional[constants.ScreenMode],
        fps: t.Optional[float] = None,
    ):
        """ Redraw photo and all UI elements
        """
        self.blit_image(img)
        if mode is not None:
            for button in self.buttons[mode]:
                self.blit_button(button)
        if fps is not None:
            self.blit_fps(fps)
        pygame.display.update()

    def get_event(
        self, screen_mode: constants.ScreenMode
    ) -> t.Optional[constants.Event]:
        """ Return an event if a button was clicked
        """
        click_position = self.input_dev.get_click()
        if click_position is not None:
            event = self.check_buttons(screen_mode, click_position)
            if event is not None:
                return event

    def check_buttons(
        self, screen_mode: constants.ScreenMode, pos: t.Tuple[int, int]
    ) -> t.Optional[constants.Event]:
        """ If there's a button at `pos`, return its event
        """
        for b in self.buttons[screen_mode]:
            if b.selected(pos):
                return b.event()
        else:
            return None

    def blit_fps(self, val: float):
        surface = self.font.render(str(round(val, 1)), False, GRAY)
        self.screen.blit(surface, FPS_OFFSET)

    def blit_button(self, button: elements.Button):
        """ Draw a button to the screen
        """
        if button.color:
            self.screen.fill(button.color, button.rect)
        for icon in (button.icon_bg, button.icon_fg):
            if icon:
                self.screen.blit(
                    icon.bitmap,
                    (
                        button.rect[0] + (button.rect[2] - icon.bitmap.get_width()) / 2,
                        button.rect[1]
                        + (button.rect[3] - icon.bitmap.get_height()) / 2,
                    ),
                )

    def blit_image(self, img: pygame.Surface):
        """ Draw an image to the screen
        """
        if img.get_width() > self.size[0] or img.get_height() > self.size[1]:
            img = pygame.transform.scale(img, self.size)
        if (
            img is None
            or img.get_width() < self.size[0]
            or img.get_height() < self.size[1]
        ):  # Letterbox, clear background
            self.screen.fill(0)

        if img:
            self.screen.blit(
                img,
                (
                    (self.size[0] - img.get_width()) / 2,
                    (self.size[1] - img.get_height()) / 2,
                ),
            )
