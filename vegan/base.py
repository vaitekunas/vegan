"""Base class that implements some functionality that most vegan classes need."""

from vegan.progress import Progress
from vegan import utils


class Base(object):
    """Implements the logging facility update."""

    """Base logging facility."""
    _log = None

    """Base progress facility."""
    _progress = None

    def __init__(self, logger=None):
        """Initialize the base class."""
        # Specify a logger
        if logger is not None and callable(logger):
            self._log = logger
        else:
            self._log = utils.simple_log

        # Specify a progressbar
        self._progress = Progress(width=32, block="#", blank=" ")
