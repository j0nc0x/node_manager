#!/usr/bin/env pythonß

"""Git Load plugin."""

import logging
import os
import subprocess

from node_manager import utils
from node_manager.plugins.base.load import Load

from git import Repo
from git.exc import NoSuchPathError, InvalidGitRepositoryError

logger = logging.getLogger(__name__)


class NodeManagerPlugin(Load):
    name = "GitLoad"

    def __init__(self):
        """Initialise the GitLoad plugin."""
        super(NodeManagerPlugin, self).__init__()
        self.manager = utils.get_manager()
        self.git_repo = None
        self.extensions = [
            ".hda",
            ".hdanc",
            ".otl",
            ".otlnc",
        ]
        logger.debug("Initialsied GitLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def clone_repo(self, path, root):
        """Clone the Node Manager repository.

        Args:
            path(str): The git path to the Node Manager repository.
            root(str): The root directory of the Node Manager repository.

        Returns:
            git.Repo: The cloned repository.
        """
        cloned_repo = None
        try:
            cloned_repo = Repo(root)
            cloned_repo.git.pull()
        except (NoSuchPathError, InvalidGitRepositoryError) as error:
            logger.debug(
                "Couldn't load repo from {path}, clone instead.".format(
                    path=root,
                )
            )
            logger.debug(error)

        if not cloned_repo:
            cloned_repo = Repo.clone_from(path, root, depth=1)

        return cloned_repo

    def build_repo(self, root, temp):
        """Build the Node Manager repository.

        Args:
            root(str): The root directory of the Node Manager repository.
            temp(str): The temp directory of the Node Manager repository.
        """
        os.makedirs(temp)
        expanded_hda_dir = os.path.join(root, "dcc", "houdini", "hda")
        for hda in os.listdir(expanded_hda_dir):
            path = os.path.join(expanded_hda_dir, hda)
            hda_path = os.path.join(temp, hda)
            logger.info("Processing {source}".format(source=path))
            hotl_cmd = ["hotl", "-C", path, hda_path]
            logger.debug(hotl_cmd)
            result = subprocess.call(hotl_cmd)
            if result != 0:
                raise RuntimeError(
                    "Failed to build HDA: {hda}".format(hda=hda)
                )

    def get_node_definition_files(self, temp):
        """Get a list of node definition files in the given directory.

        Args:
            temp(str): The directory to search for node definition files.

        Returns:
            list: A list of node definition files.
        """
        return [
            os.path.join(temp, node_definition_file)
            for node_definition_file in os.listdir(temp)
            if os.path.splitext(node_definition_file)[1] in self.extensions
        ]

    def load(self, path, root, temp):
        """Load the Node Manager repository.

        Args:
            path(str): The git path to the Node Manager repository.
            root(str): The root directory of the Node Manager repository.
            temp(str): The temp directory of the Node Manager repository.
        """
        self.git_repo = self.clone_repo(path, root)
        self.build_repo(root, temp)
        return self.get_node_definition_files(temp)
