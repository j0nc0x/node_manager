#!/usr/bin/env python

"""Validate child nodes are released."""

import pyblish.api

from node_manager import config
from node_manager import utils
from node_manager.utils import nodeutils


class ValidateChildren(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate the child nodes of the collected node."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Child nodes"
    families = ["node_manager"]

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(pyblish.plugin.Instance): The pyblish instance being processed.

        Raises:
            RuntimeError: Unreleased child node found.
        """
        node = instance.data["publish_node"]
        assert node, "No publish node found."

        for child in node.allNodes():
            if child == node:
                # Ignore the node to be published
                continue
            if nodeutils.definition_from_node(child.path()):
                # do something better than this
                path = child.type().definition().libraryFilePath()
                if not config.node_manager_config.get("released_locations", []):
                    self.log.warning(
                        "No released locations configured, skipping check."
                    )
                elif not utils.is_released(path):
                    raise RuntimeError(
                        "HDA stored in invalid location: {path}".format(
                            path=path,
                        )
                    )
