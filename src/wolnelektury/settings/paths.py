from os import path

PROJECT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
ROOT_DIR = path.dirname(path.dirname(PROJECT_DIR))
VAR_DIR = path.join(ROOT_DIR, 'var')

