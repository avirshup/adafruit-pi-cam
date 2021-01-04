import typing as t
import functools

from . import constants
from .constants import ScreenMode, Intention
from .elements import Button


def init_buttons() -> t.Dict[ScreenMode, t.List[Button]]:
    return {
        ScreenMode.image_viewer: image_viewer_buttons(),
        ScreenMode.confirm_delete: confirm_deletion_buttons(),
        ScreenMode.no_images: no_image_buttons(),
        ScreenMode.viewfinder: viewfinder_buttons(),
        ScreenMode.size_settings: size_buttons(),
        ScreenMode.effects: effects_buttons(),
        ScreenMode.set_iso: iso_buttons(),
        ScreenMode.quit: quit_buttons(),
    }


def image_viewer_buttons():
    return [
        Button.load(
            rect=(0, 188, 320, 52),
            bg_name="done",
            on_click=Intention.switch_mode,
            value=ScreenMode.viewfinder,
        ),
        Button.load(
            rect=(0, 0, 80, 52), bg_name="prev", on_click=Intention.inc_image, value=-1,
        ),
        Button.load(
            rect=(240, 0, 80, 52),
            bg_name="next",
            on_click=Intention.inc_image,
            value=1,
        ),
        Button.load(name="working", rect=(88, 70, 157, 102)),
        Button.load(name="spinner", rect=(148, 129, 22, 22)),
        Button.load(
            rect=(121, 0, 78, 52),
            bg_name="trash",
            on_click=Intention.delete_image,
            value=0,
        ),
    ]


def confirm_deletion_buttons():
    return [
        Button.load(rect=(0, 35, 320, 33), bg_name="delete"),
        Button.load(
            rect=(32, 86, 120, 100),
            bg_name="yn",
            fg_name="yes",
            on_click=Intention.confirm_delete,
            value=True,
        ),
        Button.load(
            rect=(168, 86, 120, 100),
            bg_name="yn",
            fg_name="no",
            on_click=Intention.confirm_delete,
            value=False,
        ),
    ]


def no_image_buttons():
    return [
        Button.load(
            name="screen_bg",
            rect=(0, 0, 320, 240),
            on_click=Intention.switch_mode,
            value=ScreenMode.viewfinder,
        ),
        Button.load(
            rect=(0, 188, 320, 52),
            bg_name="done",
            on_click=Intention.switch_mode,
            value=ScreenMode.viewfinder,
        ),
        Button.load(rect=(0, 53, 320, 80), bg_name="empty"),
    ]


def viewfinder_buttons():
    return [
        Button.load(
            rect=(0, 188, 156, 52),
            bg_name="gear",
            on_click=Intention.switch_mode,
            value=ScreenMode.size_settings,
        ),
        Button.load(
            rect=(164, 188, 156, 52),
            bg_name="play",
            on_click=Intention.switch_mode,
            value=ScreenMode.image_viewer,
        ),
        Button.load(
            name="viewfinder", rect=(0, 0, 320, 240), on_click=Intention.take_picture,
        ),
        Button.load(name="working", rect=(88, 51, 157, 102)),
        Button.load(name="spinner", rect=(148, 110, 22, 22)),
    ]


def size_buttons():
    return [
        Button.load(
            rect=(2, 60, 100, 120),
            bg_name="radio3-1",
            fg_name="size-l",
            on_click=Intention.set_image_size,
            value=constants.SizeMode.lg,
        ),
        Button.load(
            rect=(110, 60, 100, 120),
            bg_name="radio3-0",
            fg_name="size-m",
            on_click=Intention.set_image_size,
            value=constants.SizeMode.med,
        ),
        Button.load(
            rect=(218, 60, 100, 120),
            bg_name="radio3-0",
            fg_name="size-s",
            on_click=Intention.set_image_size,
            value=constants.SizeMode.small,
        ),
        Button.load(rect=(0, 10, 320, 29), bg_name="size"),
        *_settings_nav(),
    ]


def effects_buttons():
    return [
        Button.load(
            rect=(0, 70, 80, 52),
            bg_name="prev",
            on_click=Intention.inc_effect,
            value=-1,
        ),
        Button.load(
            rect=(240, 70, 80, 52),
            bg_name="next",
            on_click=Intention.inc_effect,
            value=1,
        ),
        Button.load(rect=(0, 67, 320, 91), bg_name="fx-none"),
        Button.load(rect=(0, 11, 320, 29), bg_name="fx"),
        *_settings_nav(),
    ]


def iso_buttons():
    return [
        Button.load(
            rect=(240, 70, 80, 52), bg_name="next", on_click=Intention.inc_iso, value=1,
        ),
        Button.load(rect=(0, 79, 320, 33), bg_name="iso-0"),
        Button.load(rect=(9, 134, 302, 26), bg_name="iso-bar"),
        Button.load(rect=(17, 157, 21, 19), bg_name="iso-arrow"),
        Button.load(rect=(0, 10, 320, 29), bg_name="iso"),
        *_settings_nav(),
    ]


def quit_buttons():
    return [
        Button.load(
            rect=(110, 60, 100, 120), bg_name="quit-ok", on_click=Intention.quit,
        ),
        Button.load(rect=(0, 10, 320, 35), bg_name="quit"),
        *_settings_nav(),
    ]


@functools.lru_cache()
def _settings_nav():
    return [
        Button.load(
            rect=(0, 0, 80, 52),
            bg_name="prev",
            on_click=Intention.inc_setting,
            value=-1,
        ),
        Button.load(
            rect=(240, 0, 80, 52),
            bg_name="next",
            on_click=Intention.inc_setting,
            value=1,
        ),
        Button.load(
            rect=(0, 188, 320, 52),
            bg_name="done",
            on_click=Intention.switch_mode,
            value=ScreenMode.viewfinder,
        ),
    ]
