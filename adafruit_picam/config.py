import typing as t
from pathlib import Path
import attr

from . import constants, util

T = t.TypeVar("T")

DEF_CAM_ROOT = Path("/opt/adacam/")
DEF_CONFIG_PATH = DEF_CAM_ROOT / "adacam.yml"

PICAM1_RES = (2592, 1944)
PICAM2_RES = (3280, 2464)


@attr.s(frozen=True, auto_attribs=True)
class Config:
    """ Immutable launch-time parameters
    """

    screensize: t.Tuple[int, int] = (320, 240)
    camera_resolution: t.Tuple[int, int] = PICAM1_RES
    fps_window: int = 10

    splash_img_path: Path = DEF_CAM_ROOT / "splash.jpg"
    splash_duration_s: float = 1

    video_driver: str = "fbcon"
    video_device: Path = Path("/dev/fb1")
    mouse_driver: str = "pitft"  # "TSLIB" if using resistive touchscreen
    mouse_device: Path = Path("/dev/input/touchscreen")

    mock_camera: bool = False

    photo_storage_dir: Path = DEF_CAM_ROOT / "photos"
    settings_cache: Path = DEF_CAM_ROOT / "settings.json"

    uid: int = attr.ib(factory=util.get_uid)
    gid: int = attr.ib(factory=util.get_gid)


@attr.s(auto_attribs=True)
class Settings:
    """ Mutable user-defined settings that are preserved between sessions
    """

    next_photo_idx: int = None
    draw_fps: bool = True
    size_mode: constants.SizeMode = constants.SizeMode.lg
    fx_mode: constants.Fx = constants.Fx.none
    iso_mode: constants.IsoSetting = constants.ISO_DATA["auto"]
    snap_pause_time: float = 2.5
    jpg_quality: float = 0.85
