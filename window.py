#!/usr/bin/env python3
import panel
import logging

# Windows display panels, which are organized in a table
# of cells that can be split horizontally and vertically.

# Each cell instance keeps track of one split
class Cell():
    def __init__(self, panel, window):
        self.window = window
        self.panel = panel
        # 2 Children come from splitting this cell either horizontally or vertically
        self.children = []
        # True for horizontal split (vertical partition), false otherwise
        self.horizontal = False
        # These record actual dimensions
        self.pos = [0, 0]
        self.dims = [0, 0]
        self.hasFocus = False

    def split(self, panel, isHorizontal = True, newIsRightOrDown = True):
        self.window.dirty = True
        newCell = Cell(panel, self.window)
        self.horizontal = isHorizontal
        thisCell = Cell(self.panel, self.window)
        self.minDims = [0, 0]
        self.growDims = [False, False]
        self.panel = None
        if newIsRightOrDown:
            self.children = [thisCell, newCell]
        else:
            self.children = [newCell, thisCell]
        # Pass focus down to eldest child
        self.children[0].hasFocus = self.hasFocus
        return self.children

    def calcMinDimsRecurse(self):
        if self.horizontal:
            prim = 0 # Index of primary dimension
            sec = 1 # Index of secondary dimension
        else:
            prim = 1
            sec = 0
        if not self.children:
            self.growDims = self.panel.growDims[:]
            self.minDims = self.panel.minDims[:]
        for child in self.children:
            child.calcMinDimsRecurse()
            self.growDims[0] |= child.growDims[0]
            self.growDims[1] |= child.growDims[1]
            self.minDims[prim] += child.minDims[prim]
            self.minDims[sec] = max(self.minDims[sec], child.minDims[sec])

    # The caller of this function already set pos and dims for this cell
    def calcDims(self):
        # These values were assigned from on high, so I must be happy with them.
        # self.pos = [x, y]
        # self.dims = [width, height]
        # I get to assign values for my children, though!
        if self.horizontal:
            prim = 0
            sec = 1
        else:
            prim = 1
            sec = 0
        # Handle the primary dimension
        # Start by giving everyone what they want
        for child in self.children:
            child.dims[prim] = child.minDims[prim]
        spaceAllocated = sum([child.dims[prim] for child in self.children])
        # Case 1: There wasn't enough to go around
        if spaceAllocated > self.dims[prim]:
            childrenToChange = self.children
        # Case 2: There is an overabundance of recources
        elif spaceAllocated < self.dims[prim]:
            childrenToChange = [child for child in self.children if child.growDims[prim]]
        # Case 3: We're all set
        else:
            childrenToChange = []
        # Actually make the change
        if childrenToChange:
            change = int((self.dims[prim] - spaceAllocated) / len(childrenToChange))
            for child in childrenToChange:
                child.dims[prim] += change
            # Reconcile roundoff error
            childrenToChange[0].dims[prim] += self.dims[prim] - sum([child.dims[prim] for child in self.children])
        # Now, handle the secondary dimension. Much easier: everybody is stuck with what we've got.
        for child in self.children:
            child.dims[sec] = self.dims[sec]
        # Position in primary dimension
        primPos = self.pos[prim]
        for child in self.children:
            child.pos[prim] = primPos
            primPos += child.dims[prim]
        # Position in secondary dimension
        for child in self.children:
            child.pos[sec] = self.pos[sec]
        # Finally, recursively call on children
        for child in self.children:
            child.calcDims()

    def draw(self, forceDraw):
        if not self.children:
            self.panel.draw(self.pos[:], self.dims[:], self.window, forceDraw)
        else:
            for child in self.children:
                child.draw(forceDraw)

    # Returns True if result is that this cell is focused
    def focus(self):
        # If this is a leaf node, then toggle focus
        if self.panel:
            self.hasFocus = not self.hasFocus
        # If not focused, then focus both me and my first child
        elif not self.hasFocus:
            self.hasFocus = True
            self.children[0].focus()
        # If focused and first child is focused and first child unfocuses, then focus second child
        elif self.children[0].hasFocus and not self.children[0].focus():
            self.children[1].focus()
        # Same as above, but second child rejects focus, then unfocus
        elif self.children[1].hasFocus and not self.children[1].focus():
            self.hasFocus = False
        return self.hasFocus

    # Return focused panel
    def getFocus(self):
        if not self.hasFocus:
            return None
        elif self.panel:
            return self.panel
        else:
            for child in self.children:
                if child.hasFocus:
                    return child.getFocus()

class Window():
    def __init__(self, cWin, rootCell, bordered = True):
        self.cWin = cWin
        self.rootCell = rootCell
        self.rotateFocus()
        self.bordered = bordered
        self.dirty = True

    def width(self):
        return self.cWin.getmaxyx()[1]

    def height(self):
        return self.cWin.getmaxyx()[0]

    def recalculateLayout(self):
        self.rootCell.calcMinDimsRecurse()
        if self.bordered:
            self.rootCell.pos = [1, 1]
            self.rootCell.dims = [self.width() - 2, self.height() - 2]
        else:
            self.rootCell.pos = [0, 0]
            self.rootCell.dims = [self.width(), self.height()]
        self.rootCell.calcDims()

    def draw(self, forceDraw = False):
        if self.dirty or forceDraw:
            self.cWin.clear()
            self.recalculateLayout()
        self.rootCell.draw(forceDraw | self.dirty)
        if (self.dirty or forceDraw) and self.bordered:
            # Top and bottom
            self.cWin.insstr(0, 0, '#' * self.width())
            self.cWin.insstr(self.height() - 1, 0, '#' * self.width())
            # Sides
            for row in range(0, self.height() - 1):
                self.cWin.addch(row, 0, '#')
                self.cWin.addch(row, self.width() - 1, '#')
            self.cWin.noutrefresh()
        self.getFocus().setBorderBold(True)
        self.dirty = False

    def rotateFocus(self):
        focused = self.getFocus()
        if focused:
            focused.setBorderBold(False)
        if not self.rootCell.focus():
            self.rootCell.focus()

    # Get focused panel
    def getFocus(self):
        return self.rootCell.getFocus()
