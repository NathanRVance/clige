#!/usr/bin/env python3
import curses
from window import Window
from window import Cell
from panel import Panel
import logging

# Various global variables for message passing
wantsStop = False

class Content():
    def __init__(self):
        pass

    def getContent(self, width, height):
        raise NotImplementedError()

    # Returns true if this content should be continuously refreshed, false if it is static content (e.g., title bar)
    def dynamic(self):
        raise NotImplementedError()

class Clige():
    # refreshMethod(mainWindow) is called before every screen refresh
    def __init__(self, refreshMethod):
        self.refreshMethod = refreshMethod
        logger = logging.basicConfig(filename='clige.log', format='%(levelname)s: %(message)s', level=logging.DEBUG)

    # initCallback(Cell) is called only once, and is intended for the initial setup. Cell contains a dummy Panel, containing an unimplemented Content.
    def startCurses(self, initCallback):
        def main(cursesWindow):
            curses.curs_set(0)
            cursesWindow.clear()
            self.mainWindow = Window(cursesWindow, Cell(Panel(Content()), None), True)
            self.mainWindow.rootCell.window = self.mainWindow
            initCallback(self.mainWindow.rootCell)
            while not wantsStop:
                self.refreshMethod(self.mainWindow)
                self.mainWindow.draw()
                curses.doupdate()
        from curses import wrapper
        wrapper(main)
