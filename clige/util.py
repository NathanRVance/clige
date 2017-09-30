#!/usr/bin/env python3
import logging
import re
import curses
tags = re.compile(r'((?<=[^\\])|^)<(.*?[^\\])>')
# This file contians utility functions for clige

def removeTags(text):
    return tags.sub('', text)

def resetTags():
    global openTags
    openTags = []

cursesTags = {'b' : curses.A_BOLD, 'i' : curses.A_DIM, 'mark' : curses.A_STANDOUT, 'u' : curses.A_UNDERLINE}

basicColors = {'black' : curses.COLOR_BLACK, 'red' : curses.COLOR_RED, 'green' : curses.COLOR_GREEN, 'yellow' : curses.COLOR_YELLOW, 'blue' : curses.COLOR_BLUE, 'magenta' : curses.COLOR_MAGENTA, 'cyan' : curses.COLOR_CYAN, 'white' : curses.COLOR_WHITE}

# name is the name used in tags, colorText and colorBack are the names of the colors for the text and the background. For example,
# defColor('bruise', 'black', 'blue') defines black text on a blue background that is used with <bruise>Bruise</bruise> tags.
def defColor(name, colorText, colorBack):
    global colors
    if not 'colors' in globals():
        colors = {}
    if not name in colors:
        colors[name] = len(colors) + 1
    curses.init_pair(colors[name], basicColors[colorText], basicColors[colorBack])

# Text is a single string containing tags, and the untagged version is aleady written at x, y
# Note: This method assumes that unclosed tags from the previous invocation are still active.
def applyTags(cWin, x, y, text):
    global openTags
    global colors
    def applyFormat(x, y, number):
        global openTags
        fmat = 0
        for tag in openTags:
            if tag in cursesTags:
                fmat |= cursesTags[tag]
            elif tag in colors:
                fmat |= curses.color_pair(colors[tag])
            else:
                fmat |= curses.A_BLINK # The penalty for improper tagging is blinking text
        cWin.chgat(y, x, number, fmat)
    def isOpen(tag):
        return tag[1] != '/'
    def tagContent(tag):
        if isOpen(tag):
            return tag[1:-1]
        else:
            return tag[2:-1]
    
    offset = 0
    while True:
        match = tags.search(text)
        if not match:
            break
        text = tags.sub('', text, count=1)
        tag = match.group()
        content = tagContent(tag)
        start = match.start()
        applyFormat(x + offset, y, start - offset)
        if isOpen(tag) and content not in openTags:
            openTags.append(content)
        elif not isOpen(tag) and content in openTags:
            openTags.remove(content)
        offset = start
    # Finally, apply any open tags to the end of the line
    applyFormat(x + offset, y, len(text) - offset)

# Attepts to cram text into an array of <= height strings, each <= width long
# If it doesn't fit, text is truncated so that it does.
# Input text is split on whitespace, so if there's some whitespace you want to preserve, don't send it through here!
def wrap(text, width, height):
    if type(text) is list:
        if max(len(removeTags(line)) for line in text) <= width and len(text) <= height:
            return text
        text = ' '.join(text)
    words = text.split()
    ret = ['']
    for word in words:
        if len(removeTags(ret[-1])) + len(removeTags(word)) + 1 > width:
            ret.append('')
        if ret[-1] != '':
            ret[-1] += ' '
        ret[-1] += word
    return ret

def centerHoriz(text, width, height):
    text = wrap(text, width, height)
    # Pad with spaces
    for index, line in enumerate(text):
        padding = int((width - len(removeTags(line))) / 2)
        text[index] = ' ' * padding + line
    return text

def centerVert(text, width, height):
    text = wrap(text, width, height)
    # Pad with blank lines
    padding = int((height - len(text)) / 2)
    text = [''] * padding + text
    return text
