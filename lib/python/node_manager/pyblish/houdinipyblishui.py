#!/usr/bin/env python

"""Houdini Pyblish UI."""

import os
import pyblish_lite
import pyblish_qml
import pyblish_qml.api

import hou


class HoudiniPyblishUI(object):
    """Houdini Pyblish UI."""

    def __init__(self, title="Houdini Pyblish", size=None, position=None):
        """Initialise the Houdini Pyblish UI.

        Args:
            title(str): The window title to use for the pyblish UI.
            size(:obj:`tuple` of :obj:`int`, :obj:`int`): The size of the pyblish UI.
            position(:obj:`tuple` of :obj:`int`, :obj:`int`): The position of the
                pyblish UI. If unset, we will attempt to centre the UI around the mouse
                cursor.
        """
        if title:
            pyblish_qml.settings.WindowTitle = title

        if size:
            pyblish_qml.settings.WindowSize = size

        if not position:
            position = self.__get_window_pos(size)
        pyblish_qml.settings.WindowPosition = position

    def __get_window_pos(self, size):
        """Determine the window position for the UI.

        Args:
            size(:obj:`tuple` of :obj:`int`, :obj:`int`): The size of the pyblish UI.

        Returns:
            (:obj:`tuple` of :obj:`int`, :obj:`int`): Window coordinates.
        """
        cursor = self.__get_cursor_pos()
        if size:
            width, height = size
            x_pos = cursor[0] - (width / 2)
            y_pos = cursor[1] - (height / 2)
            if x_pos < 0:
                x_pos = 0
            if y_pos < 0:
                y_pos = 0
            return (x_pos, y_pos)
        else:
            return cursor

    def __get_cursor_pos(self):
        """Get the cursor position from the Houdini UI.

        Returns:
            (:obj:`tuple` of :obj:`int`, :obj:`int`): Cursur coordinates.
        """
        hou_win = hou.ui.mainQtWindow()
        cursor_pos = hou_win.cursor().pos()
        return (cursor_pos.x(), cursor_pos.y())

    def launch_ui(self, lite=True):
        """
        Launch the pyblish UI
        """
        if lite:
            window = self.__lite()
        else:
            window = self.__qml()
        
        return window

    def __lite(self):
        '''launch the pyblish-lite dialoge'''
        # _register_checks()
        return pyblish_lite.show()

    def __qml(self):
        # the external python 3 with a clean env and nothing but PyQt5 and pyblish
        python3_bin = os.getenv('PYBLISH_QML_PYTHON_EXECUTABLE')
        pyblish_qml.api.register_python_executable(python3_bin)

        return pyblish_qml.show()
