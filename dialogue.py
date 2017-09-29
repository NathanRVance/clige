#!/usr/bin/env python3
import util
import clige

class exitDialogue():
    def __init__(self):
        clige.spawnWindow(30, 6, self)

    def getContent(self, width, height):
        return util.centerVert(util.centerHoriz(r'Are <i>you</i> su<b>re y</b>ou w<u>ant to <mark>quit</mark>? [y/</u>n] or other', width, height), width, height)

    def dynamic(self):
        return False

    def keyPress(self, key):
        if key == 'y':
            clige.wantsStop = True
        if key == 'y' or key == 'n':
            clige.closeWindow()
