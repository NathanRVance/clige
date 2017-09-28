#!/usr/bin/env python3
import clige
from panel import Panel
import logging

class mainContent():
    def __init__(self, contNum):
        self.contNum = contNum

    def getContent(self, width, height):
        return [''.join([str((self.contNum + x) % 10) for x in range(0, width)]) for y in range(0, height)]

    def dynamic(self):
        #return False
        return self.contNum == 3

def init(cell):
    [cell1, cell2] = cell.split(Panel(mainContent(2)), True, False)
    cell1.split(Panel(mainContent(3)), False, False)


hasRefreshed = False
def refresh(topWindow):
    global hasRefreshed
    if not hasRefreshed:
        hasRefreshed = True
        clige.spawnWindow(30, 30, mainContent(4))

def keyPress(key):
    logging.debug('Key {} pressed ({})'.format(key, ord(key)))

clige.startCurses(init, mainContent(1), refresh, keyPress)
