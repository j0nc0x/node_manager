#!/usr/bin/env python

import logging
import os

from node_manager import utils
from node_manager.plugins.base.load import Load

logger = logging.getLogger(__name__)


class NodeManagerPlugin(Load):
    name = "DefaultLoad"

    def __init__(self):
        """Initialise the DefaultLoad plugin."""
        super(NodeManagerPlugin, self).__init__()
        self.manager = utils.get_manager()
        logger.debug("Initialsied DefaultLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def get_node_definition_files(self, path):
        """Get a list of node definition files in the given directory.

        Args:
            path(str): The directory to search for node definition files.

        Returns:
            list: A list of node definition files.
        """
        return [
            os.path.join(path, node_definition_file)
            for node_definition_file in os.listdir(path)
            if os.path.splitext(node_definition_file)[1] in self.extensions
        ]

    def load(self, path, root, temp):
        """Load the Node Manager repository.

        Args:
            path(str): The git path to the Node Manager repository.
            root(str): The root directory of the Node Manager repository.
            temp(str): The temp directory of the Node Manager repository.
        """
        return self.get_node_definition_files(path)
