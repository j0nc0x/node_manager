#!/usr/bin/env python

"""Default Load Plugin that will load node definitions from a directory on disk."""

import logging
import os

from node_manager import utils

logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    """Default Load Plugin."""

    name = "DefaultLoad"
    plugin_type = "load"

    def __init__(self):
        """Initialise the DefaultLoad plugin."""
        self.manager = utils.get_manager()
        self.repo = self.manager.get_release_repo()
        self.extensions = [
            ".hda",
            ".hdanc",
            ".otl",
            ".otlnc",
        ]
        if self.repo  and self.repo.context:
            self.repo.context["repo_load_path"] = self.repo.context.get("repo_path")
        logger.debug("Initialise DefaultLoad.")

    def get_node_definition_files(self):
        """Get a list of node definition files in the given directory.

        Returns:
            list: A list of node definition files.
        """
        load_path = self.repo.context.get("repo_load_path")
        return [
            os.path.join(load_path, node_definition_file)
            for node_definition_file in os.listdir(load_path)
            if os.path.splitext(node_definition_file)[1] in self.extensions
        ]

    def load(self):
        """Load the Node Manager repository.

        Returns:
            list: A list of node definition files.
        """
        node_definition_files = self.get_node_definition_files()
        logger.debug("Loading node definition files: {files}".format(files=node_definition_files))
        return node_definition_files
