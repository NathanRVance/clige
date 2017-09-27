#!/usr/bin/env python3
import clige
from panel import Panel

class mainContent():
    def __init__(self, contNum):
        self.contNum = contNum

    def getContent(self, width, height):
        return [''.join([str((self.contNum + x) % 10) for x in range(0, width)]) for y in range(0, height)]

    def dynamic(self):
        #return False
        return self.contNum == 3

def init(cell):
    cell.panel.content = mainContent(1)
    [cell1, cell2] = cell.split(Panel(mainContent(2)), True, False)
    cell1.split(Panel(mainContent(3)), False, False)

def refresh(mainWin):
    pass


clig = clige.Clige(refresh)
clig.startCurses(init)
