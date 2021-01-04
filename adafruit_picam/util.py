import typing as t
from pathlib import Path
import json
import os
import logging

import cattr

T = t.TypeVar("T")


def dump_json(obj: t.Any, dest: Path):
    data = cattr.unstructure(obj)
    with dest.open("w") as stream:
        json.dump(data, stream)


def load_json(cl: t.Type[T], src: Path) -> T:
    with src.open("r") as stream:
        data = json.load(stream)
    obj = cattr.structure(data, cl)
    return obj


def get_uid():
    s = os.getenv("SUDO_UID")
    return int(s) if s else os.getuid()


def get_gid():
    s = os.getenv("SUDO_GID")
    return int(s) if s else os.getgid()


def make_root_logger() -> logging.Logger:
    root_logger = logging.getLogger("picam")
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(handler)
    return root_logger
