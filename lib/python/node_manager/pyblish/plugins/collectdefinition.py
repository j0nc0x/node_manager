#!/usr/bin/env python

"""Collect node definitions to validate."""

import pyblish.api

from node_manager import manager
from node_manager import utils


class CollectDefinition(pyblish.api.ContextPlugin):
    """Collect Houdini nodes based on a given dictionary of node paths."""

    order = pyblish.api.CollectorOrder
    label = "Houdini HDA - Collect"

    def process(self, context):
        """Pyblish process method.

        Args:
            context(pyblish.Context): The Houdini node instances we are validating.
        """
        manager = utils.get_manager()
        publish_node = manager.context.get("pyblish_node")
        name = publish_node.type().name()
        instance = context.create_instance(name)
        instance[:] = [publish_node]
