#!/usr/bin/env python3
import logging

# Panels display content and keep track of focus
class Panel():
    # If bordered, will take one from width and height to draw border
    def __init__(self, content, bordered = True, minWidth = 0, minHeight = 0, growWidth = True, growHeight = True):
        self.content = content
        self.bordered = bordered
        self.minDims = [minWidth, minHeight]
        self.growDims = [growWidth, growHeight]

    def draw(self, pos, dim, window, forceDraw):
        if self.content.dynamic() or forceDraw:
            cWin = window.cWin
            [x, y] = pos
            [width, height] = dim
            rightBorder = False
            bottomBorder = False
            if self.bordered:
                if x + width < window.width() - 1: # Drawing the right border
                    width -= 1
                    rightBorder = True
                if y + height < window.height() - 1: # Drawing the bottom border
                    height -= 1
                    bottomBorder = True
            content = self.content.getContent(width, height)
            for line in content[:-1]:
                cWin.addstr(y, x, line[0:width] if len(line) > width else line)
                y += 1
            # Because curses is dumb, last line must be handled differently. First, print all but the second to last character:
            lline = content[-1]
            lline = lline[0:width] if len(lline) > width else lline
            cWin.addstr(y, x, lline[0:-2])
            cWin.addch(lline[-1])
            # Then back up and insert the second to last character
            cWin.move(y, x + len(lline) - 2)
            cWin.insch(lline[-2])
            if self.bordered:
                # refresh local variables
                [x, y] = pos
                [width, height] = dim
                if rightBorder:
                    for row in range(y, y + height):
                        cWin.addch(row, x + width - 1, '+')
                if bottomBorder:
                    cWin.addstr(y + height - 1, x, '+' * (width))
            cWin.noutrefresh()
