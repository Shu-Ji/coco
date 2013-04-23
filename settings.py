#coding: u8


import os.path as osp


DB_FILE_PATH = osp.join(osp.expanduser('~'), '.cocoqq.db')

DEBUG = True
DEBUG = False


if DEBUG:
    import logging
    logging.basicConfig(level=logging.DEBUG)
