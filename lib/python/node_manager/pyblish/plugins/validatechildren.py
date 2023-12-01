#!/usr/bin/env python

"""Validate child nodes are released."""

import pyblish.api

from rbl_pipe_core.util import filesystem

from rbl_pipe_houdini.utils import nodes


class ValidateChildren(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate the child nodes of the collected node."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Child nodes"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: Unreleased child node found.
        """
        for node in instance:
            for child in node.allNodes():
                if child == node:
                    # Ignore the node to be published
                    continue
                if nodes.definition_from_node(child.path()):
                    # do something better than this
                    path = child.type().definition().libraryFilePath()
                    if not filesystem.is_released(path):
                        raise RuntimeError(
                            "HDA stored in invalid location: {path}".format(
                                path=path,
                            )
                        )
