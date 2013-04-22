#coding: u8

import os


DEBUG = False
DEBUG = True


APP_ROOT = os.path.dirname(__file__) or os.getcwd()


if DEBUG:
    import logging
    logging.basicConfig(level=logging.DEBUG)
