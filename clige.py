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
def loadConfig(confFile):
    global config
    global keys
    config = configparser.ConfigParser()
    config.read(confFile)
    keys = {}
    for key in config['keys']:
        if config['keys'][key] == 'TAB':
            keys[key] = [ord('\t')]
        elif config['keys'][key] == 'ESC':
            keys[key] = [27]
        elif config['keys'][key] == 'UP':
            keys[key] = [27, ord('['), ord('A')]
        elif config['keys'][key] == 'DOWN':
            keys[key] = [27, ord('['), ord('B')]
        elif config['keys'][key] == 'RIGHT':
            keys[key] = [27, ord('['), ord('C')]
        elif config['keys'][key] == 'LEFT':
            keys[key] = [27, ord('['), ord('D')]
        else:
            value = config['keys'][key]
            if len(value) != 1:
                raise ValueError('Value "{0}" inappropriate as a keybinding for "{1}"'.format(value, key))
            keys[key] = [ord(value)]
        
# initCallback(Cell) is called only once, and is intended for the initial setup.
# refreshMethod(mainWindow) is called before every screen refresh
def startCurses(initCallback, initContent, refreshMethod):
    global config
    logging.basicConfig(filename=config['clige']['logfile'], format='%(levelname)s: %(message)s', level=logging.DEBUG)
    global windowStack
    windowStack = []
    def main(cWin):
        global forceDraw
        global wantsStop
        forceDraw, wantsStop = False, False
        curses.curs_set(0)
        cWin.clear()
        cWin.timeout(25)
        windowStack.append(Window(cWin, Cell(Panel(initContent), None), False))
        windowStack[0].rootCell.window = windowStack[0]
        initCallback(windowStack[0].rootCell)
        while not wantsStop:
            procInput(windowStack[-1])
            refreshMethod(windowStack[-1])
            windowStack[-1].draw(forceDraw)
            forceDraw = False
            curses.doupdate()
    from curses import wrapper
    wrapper(main)

# Process input
def procInput(window):
    # Ends up containing a sequence of keys that translate to an operation
    inp = []
    while True:
        ch = window.cWin.getch()
        if ch != -1:
            inp.append(ch)
        else:
            break
    # Much of this control flow isn't utilized.
    # TODO: Somehow, check for pressed keys, not just inputs. This is necessary for action games.
    # Unfortunately, there may not exist a portable way to do this. Perhaps just for Linux?
    # Supposedly, MidnightCommander implements this (just for Linux).
    global keys
    functions = [function for function in keys if keys[function] == inp]
    for function in functions:
        if function == 'switch_focus':
            window.rotateFocus()
        elif function == 'close_window':
            closeWindow()
        else:
            windowStack[-1].getFocus().content.keyPress(function)
    else:
        if inp:
            # Just send along the key value of inp
            windowStack[-1].getFocus().content.keyPress(chr(inp[0]))

def width():
    return windowStack[0].width()

def height():
    return windowStack[0].height()

def closeWindow():
    if len(windowStack) == 1:
        import dialogue
        dialogue.exitDialogue()
    else:
        del windowStack[-1]
        global forceDraw
        forceDraw = True

def spawnWindow(winWidth, winHeight, content):
    if winWidth > width():
        winWidth = width()
    if winHeight > height():
        winHeight = height()
    newCWin = curses.newwin(winHeight, winWidth, int((height() - winHeight) / 2), int((width() - winWidth) / 2))
    newCWin.timeout(25)
    windowStack.append(Window(newCWin, Cell(Panel(content), None), True))
    windowStack[-1].rootCell.window = windowStack[-1]
    return windowStack[-1].rootCell
