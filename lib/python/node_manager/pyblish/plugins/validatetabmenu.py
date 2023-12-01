#!/usr/bin/env python

"""Validate tab menu."""

import re

import pyblish.api


class ValidateTabMenu(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate whether a valid tab menu has been specified."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Tab Menu"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: Invalid or missing tab menu set.
        """
        for node in instance:
            definition = node.type().definition()
            tools_shelf = definition.sections().get("Tools.shelf")
            submenu_regex = re.compile(r"<toolSubmenu>(.*)</toolSubmenu>")
            match = submenu_regex.search(tools_shelf.contents())
            if not match:
                raise RuntimeError(
                    "No toolSubmenu entry found in Tools.shelf for {nodetype}".format(
                        nodetype=node.type().name(),
                    )
                )
            if not match.group(1) != "Digital Assets":
                raise RuntimeError("Invalid toolSubmenu used of 'Digital Assets'")
