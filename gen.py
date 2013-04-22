#! /usr/bin/env python


def run():
    import os
    os.system("pyrcc4 -o rsrc_rc.py res/rsrc.qrc")
    os.system("pyuic4 -o window.py res/window.ui")
