#!/usr/bin/env python

"""Pyblish Validate Plugin."""

import logging
import os

import pyblish.api

from node_manager import utils
from node_manager.pyblish import houdinipyblishui


logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    """Pyblush Validate Plugin."""

    name = "PyblishValidate"
    plugin_type = "validate"

    def __init__(self):
        """Initialise the DefaultValidate plugin."""
        self.manager = utils.get_manager()
        logger.debug("Initialise PyblishValidate.")

    def validate(self, current_node):
        """A very basic Houdini HDA validator.

        Args:
            current_node(hou.Node): The node to validate.        

        Returns:
            bool: True if the node is ready to release.
        """
        # Make sure we don't already have plugins loaded from elsewhere
        pyblish.api.deregister_all_paths()
        pyblish.api.deregister_all_plugins()

        # Make the node to be published available for collection
        self.manager.context["pyblish_node"] = current_node
        logger.debug("Publish node = {node}".format(node=current_node))

        # Register the application host
        pyblish.api.register_host("houdini")

        # Register the plugins
        module_root = self.manager.context.get("manager_module_root")
        plugins_path = os.path.join(module_root, "pyblish", "plugins")
        logger.debug("Registering Pyblish plugins from: {path}".format(path=plugins_path))
        pyblish.api.register_plugin_path(plugins_path)

        # Launch the UI
        validator = houdinipyblishui.HoudiniPyblishUI(
            title="HDA Manager Validator",
            size=(800, 500),
        )
        self.manager.context["pyblish_ui"] = validator.launch_ui()        
