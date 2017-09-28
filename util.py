#!/usr/bin/env python3

# This file contians utility functions for clige

# Attepts to cram text into an array of <= height strings, each <= width long
# If it doesn't fit, text is truncated so that it does.
# Input text is split on whitespace, so if there's some whitespace you want to preserve, don't send it through here!
def wrap(text, width, height):
    if type(text) is list:
        if max(len(line) for line in text) <= width and len(text) <= height:
            return text
        text = ' '.join(text)
    words = text.split()
    ret = ['']
    for word in words:
        if len(ret[-1]) + len(word) + 1 > width:
            ret.append('')
        if ret[-1] != '':
            ret[-1] += ' '
        ret[-1] += word
    return ret

def centerHoriz(text, width, height):
    text = wrap(text, width, height)
    # Pad with spaces
    for index, line in enumerate(text):
        padding = int((width - len(line)) / 2)
        text[index] = ' ' * padding + line + ' ' * padding
    return text

def centerVert(text, width, height):
    text = wrap(text, width, height)
    # Pad with blank lines
    padding = int((height - len(text)) / 2)
    text = [''] * padding + text
    return text
