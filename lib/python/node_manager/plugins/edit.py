#!/usr/bin/env python

"""Default Edit Plugin."""

import logging
import os

from node_manager import utils

logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    """Default Edit Plugin."""

    name = "DefaultEdit"
    plugin_type = "edit"

    def __init__(self, current_node, major=False, minor=False,):
        """Initialise the plugin.

        Args:
            current_node(hou.Node): The node to edit.
            major(bool): Whether to increment the major version.
            minor(bool): Whether to increment the minor version. 
        """
        self.manager = utils.get_manager()
        self.current_node = current_node
        self.major = major
        self.minor = minor

        logger.debug(
            "Initialise DefaultLoad: {repo_path}".format(
                repo_path=self.repo.context.get("repo_path"),
            )
        )

    def edit_definition(self):
        pass
