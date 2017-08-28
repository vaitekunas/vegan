"""Simplistic progressbar."""

import math


class Progress(object):
    """Displays a progress bar."""

    _width = 32
    _block = "#"
    _blank = "-"

    def __init__(self, width=32, block="#", blank="-"):
        """Initialize the progressbar."""
        self._width = width
        self._block = block
        self._blank = blank

        self.reset()

    def reset(self):
        """Reset the progressbar."""
        print("\n\r", end="", flush=True)

    def set(self, i, total):
        """Set progressbar value."""
        value = max(0, min(1, i/total))

        blocks = math.ceil(self._width*value)
        print('\rParsing emails: [%s%s] %s (%d/%d)' % (
               self._block*blocks,
               self._blank*(self._width-blocks),
               str(round(i/total*100, 2))+'%',
               i,
               total), end='', flush=True
              )
