import sys
import os
import shutil

ELPHI_ROOT = None
TEST_ROOT = None
OUTPUT_DIR = None


def init():
    global ELPHI_ROOT
    global TEST_ROOT
    global OUTPUT_DIR
    TEST_ROOT = os.path.abspath(os.path.dirname(__file__))
    ELPHI_ROOT = os.path.dirname(TEST_ROOT)
    if sys.path[0] != ELPHI_ROOT:
        sys.path.insert(0, ELPHI_ROOT)

    OUTPUT_DIR = os.path.join(TEST_ROOT, "output")
    if os.path.isdir(OUTPUT_DIR):
        for item in os.listdir(OUTPUT_DIR):
            name = os.path.join(OUTPUT_DIR, item)
            if os.path.isdir(name):
                shutil.rmtree(name)
            else:
                os.remove(name)
    else:
        os.makedirs(OUTPUT_DIR)

init()


def output_name(*args):
    return os.path.join(OUTPUT_DIR, *args)
