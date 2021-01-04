# Point-and-shoot camera for Raspberry Pi w/camera and Adafruit PiTFT.
# This must run as root (sudo python cam.py) due to framebuffer, etc.
#
# Adafruit invests time and resources providing this open source code,
# please support Adafruit and open-source development by purchasing
# products from Adafruit, thanks!
#
# http://www.adafruit.com/products/998  (Raspberry Pi Model B)
# http://www.adafruit.com/products/1367 (Raspberry Pi Camera Board)
# http://www.adafruit.com/products/1601 (PiTFT Mini Kit)
# This can also work with the Model A board and/or the Pi NoIR camera.
#
# Prerequisite tutorials: aside from the basic Raspbian setup and
# enabling the camera in raspi-config, you should configure WiFi (if
# using wireless with the Dropbox upload feature) and read these:
# PiTFT setup (the tactile switch buttons are not required for this
# project, but can be installed if you want them for other things):
# http://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi
# Dropbox setup (if using the Dropbox upload feature):
# http://raspi.tv/2013/how-to-use-dropbox-with-raspberry-pi
#
# Written by Phil Burgess / Paint Your Dragon for Adafruit Industries.
# BSD license, all text above must be included in any redistribution.
#
# Ported to Python 3 and refactored by AMV, 12/2020
import time
from pathlib import Path
import click

from . import root_logger
from . import config, util
from .event_handlers import handle_event
from .state import State
from .ui import UI

LOGGER = root_logger.getChild("main")


@click.command("adacam")
@click.argument("cfg_path", default=config.DEF_CONFIG_PATH)
@click.option(
    "-l",
    "--loglevel",
    help="Set logging level",
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="warning",
)
def entrypoint(cfg_path: Path = config.DEF_CONFIG_PATH, loglevel: str = "warning"):
    f""" Start the webcam process. Must run as root.
    
    Args:
        cfg_path: Path to config file (default: {config.DEF_CONFIG_PATH})
    """
    root_logger.setLevel(loglevel.upper())
    try:
        cfg = util.load_json(config.Config, cfg_path)
    except FileNotFoundError:
        LOGGER.warning(f"No config file found at {cfg_path}; using defaults")
        cfg = config.Config()
    main(cfg)


def main(cfg: config.Config):
    """ Run the app's lifecycle as configured
    """
    LOGGER.critical("startup")
    LOGGER.info(f"Config: {cfg}")

    state = State.initialize(cfg)
    ui = UI.initialize(cfg)

    try:
        if cfg.splash_img_path and cfg.splash_img_path.is_file():
            import pygame.image

            img = pygame.image.load(str(cfg.splash_img_path))
            ui.redraw(img, mode=None)
            time.sleep(cfg.splash_duration_s)
    except Exception as exc:
        LOGGER.error("splash error", exc_info=True)

    with state.cleanup(), ui.cleanup():
        try:
            run_forever(ui, state)
        except KeyboardInterrupt:
            LOGGER.warning("caught keyboard interrupt, shutting down")
        except Exception as exc:
            LOGGER.error("Exiting: unhandled exception", exc_info=True)
        else:
            LOGGER.info("Loop exited normally")

    LOGGER.critical("shutdown")


def run_forever(ui: UI, state: State):
    """ Main loop.

    Runs until an unhandled exception (including KeyboardInterrupt) or ``state.shutdown is True``
    """

    while not state.shutdown:
        fps = state.fps_tick()

        # react to user input events
        event = ui.get_event(state.screen_mode)
        if event is not None:
            LOGGER.debug(f"Event: {event}")
            handle_event(state, event)

        # need some sort of lockout or debounce

        # draw screen
        img = state.get_display_image()
        if state.took_picture:
            ui.redraw(img, mode=None)
            time.sleep(state.settings.snap_pause_time)
            state.took_picture = False
        else:
            ui.redraw(
                img, state.screen_mode, fps=fps if state.settings.draw_fps else None
            )
