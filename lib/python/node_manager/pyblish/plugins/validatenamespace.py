#!/usr/bin/env python

"""Validate node namespace."""

import pyblish.api

from node_manager import utils


class ValidateNamespace(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate the namespace of the collected node."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Namespace"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: Invalid namespace found.
        """
        for node in instance:
            definition = node.type().definition()
            man = utils.get_manager()
            if not man.valid_namespace(definition):
                raise RuntimeError(
                    "Invalid namespace for {node}".format(
                        node=node.type().name(),
                    )
                )
