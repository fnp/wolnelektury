from os.path import abspath, join, exists
from shutil import rmtree
from waiter.settings import WAITER_ROOT


def check_abspath(path):
    abs_path = abspath(join(WAITER_ROOT, path))
    if not abs_path.startswith(WAITER_ROOT):
        raise ValueError('Path not inside WAITER_ROOT.')
    return abs_path


def clear_cache(path):
    abs_path = check_abspath(path)
    if exists(abs_path):
        rmtree(abs_path)
    
