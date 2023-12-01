#!/usr/bin/env python

"""Validate node is HDA."""

import pyblish.api

from node_manager.utils import nodeutils


class ValidateIsHDA(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate if the collected node is a HDA."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Is digital asset"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: Node is not a HDA.
        """
        for node in instance:
            if not nodeutils.definition_from_node(node.path()):
                raise RuntimeError("Node is not a HDA.")
