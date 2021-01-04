# -*- coding: utf-8 -*-
#  piTFT touchscreen handling using evdev
"""
This file is a modified copy of pitft_touchscreen.py, originally from:
Repository: https://github.com/pigamedrv/pitft_touchscreen
Commit: 1111a18989bfa5cca50fbcae333312840063d8ea

Copyright PiGameDrv, licensed under GPL v3 (see GPLv3.txt in this directory)
"""

import os
import typing as t
import atexit

import evdev

import threading

try:
    # python 3.5+
    import queue
except ImportError:
    # python 2.7
    import Queue as queue


# Class for handling events from piTFT
class pitft_touchscreen:
    def __init__(
        self, device_path=os.getenv("PIGAME_TS") or "/dev/input/touchscreen", grab=False
    ):
        super(pitft_touchscreen, self).__init__()
        self.device_path = device_path
        self.grab = grab
        self.events = queue.Queue()
        self.shutdown = threading.Event()
        self.thread = threading.Thread(target=self.process_device, daemon=True)
        self.thread.daemon = True
        atexit.register(self.shutdown.set)

    def start(self):
        assert not self.thread.is_alive()
        self.thread.start()

    def shutdown(self, timeout: t.Optional[float]):
        self.shutdown.set()
        self.thread.join(timeout=timeout)

    # thread function
    def process_device(self):
        device = None
        # if the path to device is not found, InputDevice raises an OSError
        # exception.  This will handle it and close thread.
        try:
            device = evdev.InputDevice(self.device_path)
            if self.grab:
                device.grab()
        except Exception as ex:
            message = (
                "Unable to load device {0} due to a {1} exception with"
                " message: {2}.".format(self.device_path, type(ex).__name__, str(ex))
            )
            raise Exception(message)
        finally:
            if device is None:
                self.shutdown.set()
        # Loop for getting evdev events
        event = {"time": None, "id": None, "x": None, "y": None, "touch": None}
        dropping = False
        while not self.shutdown.is_set():
            for input_event in device.read_loop():
                if input_event.type == evdev.ecodes.EV_ABS:
                    if input_event.code == evdev.ecodes.ABS_X:
                        event["x"] = input_event.value
                    elif input_event.code == evdev.ecodes.ABS_Y:
                        event["y"] = input_event.value
                    elif input_event.code == evdev.ecodes.ABS_MT_TRACKING_ID:
                        event["id"] = input_event.value
                        if input_event.value == -1:
                            event["x"] = None
                            event["y"] = None
                            event["touch"] = None
                    elif input_event.code == evdev.ecodes.ABS_MT_POSITION_X:
                        pass
                    elif input_event.code == evdev.ecodes.ABS_MT_POSITION_Y:
                        pass
                elif input_event.type == evdev.ecodes.EV_KEY:
                    event["touch"] = input_event.value
                elif input_event.type == evdev.ecodes.SYN_REPORT:
                    if dropping:
                        event["x"] = None
                        event["y"] = None
                        event["touch"] = None
                        dropping = False
                    else:
                        event["time"] = input_event.timestamp()
                        self.events.put(event)
                        e = event
                        event = {"x": e["x"], "y": e["y"]}
                        try:
                            event["id"] = e["id"]
                        except KeyError:
                            event["id"] = None
                        try:
                            event["touch"] = e["touch"]
                        except KeyError:
                            event["touch"] = None
                elif input_event.type == evdev.ecodes.SYN_DROPPED:
                    dropping = True
        if self.grab:
            device.ungrab()

    def get_events(self):
        while not self.events.empty():
            yield self.events.get()
