import sys
import shutil
from pathlib import Path, PosixPath

def check_cmd_exist(command):
    return shutil.which(command) is not None

def importpath(path):
    if type(path) is not PosixPath:
        strpath = str(path)
        if not strpath.startswith("/"):
            parent_path = Path(sys._getframe().f_globals.get("__file__", ".")).parent
            path = parent_path / path
        else:
            path = Path(path)

    try:
        sys.path.insert(0, str(path.parent))
        module = __import__(path.stem)
    finally:
        sys.path.pop(0)
    return module
