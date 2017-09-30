#!/usr/bin/env python3
import logging
import curses
from clige import util

# Panels display content and keep track of focus
class Panel():
    # If bordered, will take one from width and height to draw border
    def __init__(self, content, bordered = True, minWidth = 0, minHeight = 0, growWidth = True, growHeight = True):
        self.content = content
        self.bordered = bordered
        self.minDims = [minWidth, minHeight]
        self.growDims = [growWidth, growHeight]

    def draw(self, pos, dim, window, forceDraw):
        self.pos = pos
        self.dim = dim
        self.window = window
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
            util.resetTags()
            for line in content[:-1]:
                untagged = util.removeTags(line)
                cWin.addstr(y, x, untagged[0:width] if len(untagged) > width else untagged)
                util.applyTags(cWin, x, y, line)
                y += 1
            # Because curses is dumb, last line must be handled differently. First, print all but the second to last character:
            lline = content[-1]
            untagged = util.removeTags(lline)
            untagged = untagged[0:width] if len(untagged) > width else untagged
            cWin.addstr(y, x, untagged[0:-2])
            cWin.addch(untagged[-1])
            # Delete the next character
            cWin.delch(y, x + len(untagged) - 1)
            # Then back up and insert the second to last character
            cWin.move(y, x + len(untagged) - 2)
            cWin.insch(untagged[-2])
            util.applyTags(cWin, x, y, lline)
            if self.bordered and forceDraw:
                # refresh local variables
                [x, y] = pos
                [width, height] = dim
                if rightBorder:
                    for row in range(y, y + height):
                        cWin.addch(row, x + width - 1, '+')
                if bottomBorder:
                    cWin.addstr(y + height - 1, x, '+' * (width))
            cWin.noutrefresh()

    def setBorderBold(self, borders):
        if borders:
            attribute = curses.A_BOLD
        else:
            attribute = curses.A_NORMAL
        # Borders (if they exist) are at pos - 1, and pos + dim - 1.
        # For now, assume that borders exist
        cWin = self.window.cWin
        top = self.pos[1] - 1
        bot = self.pos[1] + self.dim[1]
        left = self.pos[0] - 1
        right = self.pos[0] + self.dim[0]
        winHeight = self.window.height()
        winWidth = self.window.width()
        if right < winWidth - 1:
            right -= 1
        if bot < winHeight - 1:
            bot -= 1
        # First, do top and bottom borders
        if top >= 0:
            cWin.chgat(top, left + 1, right - left - 1, attribute)
        if bot < winHeight:
            cWin.chgat(bot, left + 1, right - left - 1, attribute)
        # Then, traverse the sides:
        if top < 0:
            top = 0
        if bot + 1 > winHeight:
            bot = winHeight - 1
        for y in range(top, bot + 1):
            if left >= 0:
                cWin.chgat(y, left, 1, attribute)
            if right < winWidth:
                cWin.chgat(y, right, 1, attribute)
