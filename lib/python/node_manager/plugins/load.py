#!/usr/bin/env python

import logging
import os

from node_manager import utils

logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    name = "DefaultLoad"
    plugin_type = "load"

    def __init__(self):
        """ 
        """
        self.manager = utils.get_manager()
        logger.debug("Initialise DefaultLoad.")

        self.extensions = [
            ".hda",
            ".hdanc",
            ".otl",
            ".otlnc",
        ]

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

    def load(self, path):
        """Load the Node Manager repository.

        Args:
            path(str): The path to the Node Manager repository.
            root(str): The root directory of the Node Manager repository.
            temp(str): The temp directory of the Node Manager repository.
        """
        return self.get_node_definition_files(path)
