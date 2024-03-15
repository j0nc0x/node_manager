#!/usr/bin/env python

"""Default Validate Plugin."""

import logging

from node_manager import utils
from node_manager.utils import nodeutils


logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    """Default Validate Plugin."""

    name = "DefaultValidate"
    plugin_type = "validate"

    def __init__(self):
        """Initialise the DefaultValidate plugin."""
        self.manager = utils.get_manager()
        logger.debug("Initialise DefaultValidate.")

    def validate(self, current_node):
        """A very basic Houdini HDA validator.

        Args:
            current_node(hou.Node): The node to validate.        

        Returns:
            bool: True if the node is ready to release.
        """
        # Is the node a digital asset?
        if not nodeutils.is_digital_asset(current_node.path()):
            logger.warning("Node is not a digital asset.")
            return False

        # Is the node definition saved?
        if current_node.isEditable():
            logger.warning("Node definition is not saved.")
            return False

        logger.info("Node is ready to release.")

        # Run the publish
        self.manager.publish_definition(current_node)
