#!/usr/bin/env python3
import curses
from window import Window
from window import Cell
from panel import Panel
import logging
import configparser
import os
os.environ.setdefault('ESCDELAY', '25')

# Various global variables for message passing
wantsStop = False
forceDraw = False
windowStack = []
config = configparser.ConfigParser()
config.read('config')
keys = config['keys']
for key in keys:
    if keys[key] == 'TAB':
        keys[key] = '\t'
    elif keys[key] == 'ESC':
        keys[key] = chr(27)
        
# initCallback(Cell) is called only once, and is intended for the initial setup.
# refreshMethod(mainWindow) is called before every screen refresh
def startCurses(initCallback, initContent, refreshMethod, keyPressCallback):
    logging.basicConfig(filename=config['DEFAULT']['logfile'], format='%(levelname)s: %(message)s', level=logging.DEBUG)
    global windowStack
    def main(cWin):
        global forceDraw
        global wantsStop
        curses.curs_set(0)
        cWin.clear()
        cWin.nodelay(1)
        windowStack.append(Window(cWin, Cell(Panel(initContent), None), False))
        windowStack[0].rootCell.window = windowStack[0]
        initCallback(windowStack[0].rootCell)
        while not wantsStop:
            procInput(windowStack[-1], keyPressCallback)
            refreshMethod(windowStack[-1])
            windowStack[-1].draw(forceDraw)
            forceDraw = False
            curses.doupdate()
    from curses import wrapper
    wrapper(main)

# Process input
def procInput(window, inputCallback):
    try:
        while True:
            key = window.cWin.getkey()
            if key == config['keys']['switch_focus']:
                window.rotateFocus()
            elif key == config['keys']['close_window']:
                if len(windowStack) == 1:
                    global wantsStop
                    wantsStop = True
                else:
                    del windowStack[-1]
                    forceDraw = True
            else:
                inputCallback(key)
    except curses.error:
        pass

def width():
    return windowStack[0].width()

def height():
    return windowStack[0].height()

def spawnWindow(winWidth, winHeight, content):
    if winWidth > width():
        winWidth = width()
    if winHeight > height():
        winHeight = height()
    newCWin = curses.newwin(winHeight, winWidth, int((height() - winHeight) / 2), int((width() - winWidth) / 2))
    newCWin.nodelay(1)
    windowStack.append(Window(newCWin, Cell(Panel(content), None), True))
    windowStack[-1].rootCell.window = windowStack[-1]
    return windowStack[-1].rootCell
