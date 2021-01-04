from . import _version

__version__ = _version.get_versions()["version"]


from . import util

root_logger = util.make_root_logger()
