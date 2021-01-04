import typing as t

from . import root_logger
from .constants import Intention, ScreenMode
from . import constants

if t.TYPE_CHECKING:
    from .state import State


Fn = t.TypeVar("Fn", bound=t.Callable)
LOGGER = root_logger.getChild("events")


def handle_event(state: "State", event: constants.Event) -> None:
    """ dispatch event to the appropriate handler
    """
    HANDLERS[event.intention](state, event.value)


def _handler(intention: Intention) -> t.Callable[[Fn], Fn]:
    def register(f: Fn) -> Fn:
        assert intention not in HANDLERS
        HANDLERS[intention] = f
        return f

    return register


HANDLERS = {}

#############################
# Mode switch handlers      #
#############################
@_handler(Intention.switch_mode)
def switch_mode(state: "State", new_mode: ScreenMode):
    # sanity check
    LOGGER.info(f"Change mode: {state.screen_mode.value} -> {new_mode.value}")
    if new_mode is state.screen_mode:
        LOGGER.warning("Changing from mode to itself")
        return

    state.last_screen_mode = state.screen_mode
    state.screen_mode = new_mode


#############################
# Taking pictures           #
#############################
@_handler(Intention.take_picture)
def take_picture(state: "State", _):
    if state.image_ids:
        target_id = state.image_ids[-1] + 1
    else:
        target_id = 0
    with state.storage.write_image(target_id) as stream:
        state.camera.write_picture(stream, state.settings)
    LOGGER.info(f"New picture: {target_id}")
    state.selected_image_index = -1
    state.image_ids.add(target_id)
    state.took_picture = True


#############################
# Image viewer handlers     #
#############################
@_handler(Intention.inc_image)
def increment_image(state: "State", increment: int):
    new_idx = (state.selected_image_index + increment) % len(state.image_ids)
    state.selected_image_index = new_idx
    state.load_image()


@_handler(Intention.delete_image)
def delete_image(state: "State", _):
    image_id = state.image_ids[state.selected_image_index]
    state.storage.delete_image(image_id)


@_handler(Intention.inc_setting)
def cycle_settings_view(state: "State", increment: int):
    state.setting_idx = (state.setting_idx + increment) % len(constants.SETTINGS_MODES)
    new_mode = constants.SETTINGS_MODES[state.setting_idx]
    switch_mode(state, new_mode)


@_handler(Intention.inc_iso)
def change_iso():
    raise NotImplementedError()
