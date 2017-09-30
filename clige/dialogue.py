#!/usr/bin/env python3
from clige import util
from clige import clige

class exitDialogue():
    def __init__(self):
        clige.spawnWindow(30, 6, self)
        util.defColor('rb', 'red', 'green')

    def getContent(self, width, height):
        return util.centerVert(util.centerHoriz(r'Are you sure you want to quit? [y/n]', width, height), width, height)

    def dynamic(self):
        return False

    def keyPress(self, key):
        if key == 'y':
            clige.wantsStop = True
        if key == 'y' or key == 'n':
            clige.closeWindow()
