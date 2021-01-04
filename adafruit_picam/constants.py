import typing as t
from enum import Enum
import attr


class ScreenMode(Enum):
    image_viewer = "image_viewer"
    confirm_delete = "confirm_delete"
    no_images = "no_images"
    viewfinder = "viewfinder"
    size_settings = "size_settings"
    effects = "effects"
    set_iso = "set_iso"
    quit = "quit"


SETTINGS_MODES = (ScreenMode.size_settings, ScreenMode.effects, ScreenMode.set_iso)


class Intention(Enum):
    quit = "quit"

    delete_image = "delete_image"
    confirm_delete = "confirm_delete"

    take_picture = "take_picture"

    switch_mode = "switch_mode"

    set_image_size = "set_image_size"

    inc_image = "inc_image"
    inc_setting = "inv_setting"
    inc_effect = "inc_effect"
    inc_iso = "inc_iso"


@attr.s(frozen=True, auto_attribs=True)
class Event:
    intention: Intention
    value: t.Any


class Fx(Enum):
    """
    A fixed list of image effects is used (rather than polling
    camera.IMAGE_EFFECTS) because the latter contains a few elements
    that aren't valid (at least in video_port mode) -- e.g. blackboard,
    whiteboard, posterize (but posterise, British spelling, is OK).
    Others have no visible effect (or might require setting add'l
    camera parameters for which there's no GUI yet) -- e.g. saturation,
    colorbalance, colorpoint.
    """

    none = "none"
    sketch = "sketch"
    gpen = "gpen"
    pastel = "pastel"
    watercolor = "watercolor"
    oilpaint = "oilpaint"
    hatch = "hatch"
    negative = "negative"
    colorswap = "colorswap"
    posterise = "posterise"
    denoise = "denoise"
    blur = "blur"
    film = "film"
    washedout = "washedout"
    emboss = "emboss"
    cartoon = "cartoon"
    solarize = "solarize"


#######################
# Image size settings #
#######################


class SizeMode(Enum):
    """ Inverse size of pictures to store
    """

    small = 4
    med = 2
    lg = 1


################
# ISO settings #
################
@attr.s(frozen=True, auto_attribs=True)
class IsoSetting:
    iso: t.Union[int, str]
    x_pos: int


ISO_DATA = {
    iso: IsoSetting(iso, xpos)
    for iso, xpos in (
        ["auto", 137],
        [0, 27],
        [100, 64],
        [200, 97],
        [320, 137],
        [400, 164],
        [500, 197],
        [640, 244],
        [800, 297],
    )
}
