#!/usr/bin/env pythonß

"""Git Load plugin."""

import logging
import os
import subprocess

from node_manager import utils
from node_manager.plugins import load

from git import Repo
from git.exc import NoSuchPathError, InvalidGitRepositoryError

logger = logging.getLogger(__name__)


class NodeManagerPlugin(load.NodeManagerPlugin):
    name = "GitLoad"

    def __init__(self):
        """Initialise the GitLoad plugin."""
        super(NodeManagerPlugin, self).__init__()
        self.git_repo = None
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

    def load(self, path, root, temp):
        """Load the Node Manager repository.

        Args:
            path(str): The git path to the Node Manager repository.
            root(str): The root directory of the Node Manager repository.
            temp(str): The temp directory of the Node Manager repository.
        """
        self.git_repo = self.clone_repo(path, root)
        self.build_repo(root, temp)
        return super(NodeManagerPlugin, self).load(temp)
