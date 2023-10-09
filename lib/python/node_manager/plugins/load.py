#!/usr/bin/env python

"""Default Load Plugin."""

import logging
import os

from node_manager import utils

logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    name = "DefaultLoad"
    plugin_type = "load"

    def __init__(self, repo):
        """ 
        """
        self.repo = repo
        self.manager = utils.get_manager()
        logger.debug(
            "Initialise DefaultLoad: {repo_path}".format(
                repo_path=self.get_repo_load_path(),
            )
        )

        self.extensions = [
            ".hda",
            ".hdanc",
            ".otl",
            ".otlnc",
        ]

    def get_repo_load_path(self):
        """Get the path on disk to load the repository from.

        Returns:
            str: The path on disk to load the repository from.
        """
        return self.repo.repo_path

    def get_node_definition_files(self):
        """Get a list of node definition files in the given directory.

        Args:
            path(str): The directory to search for node definition files.

        Returns:
            list: A list of node definition files.
        """
        return [
            os.path.join(self.get_repo_load_path(), node_definition_file)
            for node_definition_file in os.listdir(self.get_repo_load_path())
            if os.path.splitext(node_definition_file)[1] in self.extensions
        ]

    def load(self):
        """Load the Node Manager repository."""
        node_definition_files = self.get_node_definition_files()
        logger.debug("Loading node definition files: {files}".format(files=node_definition_files))
        return node_definition_files
