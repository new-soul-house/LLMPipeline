import shutil

def check_cmd_exist(command):
    return shutil.which(command) is not None
