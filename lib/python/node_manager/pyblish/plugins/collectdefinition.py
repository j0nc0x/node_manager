#!/usr/bin/env python

"""Collect node definitions to validate."""

import pyblish.api

from node_manager import utils


class CollectDefinition(pyblish.api.ContextPlugin):
    """Collect Houdini nodes based on a given dictionary of node paths."""

    order = pyblish.api.CollectorOrder
    label = "Houdini HDA - Collect"
    families = ["node_manager"]

    def process(self, context):
        """Pyblish process method.

        Args:
            context(pyblish.Context): The Houdini node instances we are validating.
        """
        manager = utils.get_manager()
        publish_node = manager.context.get("pyblish_node")
        instance_data = {
            "name": publish_node.type().name(),
            "family": "node_manager",
        }

        instance = context.create_instance(
            instance_data.get("name"),
            family=instance_data.get("family"),
        )
        instance[:] = [instance_data]
        instance.data["publish_node"] = publish_node
