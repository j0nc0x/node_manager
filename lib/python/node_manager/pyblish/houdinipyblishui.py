#!/usr/bin/env python

"""Houdini Pyblish UI."""

import pyblish_lite


class HoudiniPyblishUI(object):
    """Houdini Pyblish UI."""

    def __init__(self, title="Houdini Pyblish", size=None):
        """Initialise the Houdini Pyblish UI.

        Args:
            title(str): The window title to use for the pyblish UI.
            size(:obj:`tuple` of :obj:`int`, :obj:`int`): The size of the pyblish UI.
        """
        pyblish_lite.settings.WindowTitle = title
        pyblish_lite.settings.WindowSize = size

    def launch_ui(self):
        """
        Launch the pyblish UI
        """
        return pyblish_lite.show()
