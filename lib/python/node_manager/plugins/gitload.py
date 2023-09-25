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

    def __init__(self, repo_path, repo_root, repo_temp):
        """Initialise the GitLoad plugin."""
        super(NodeManagerPlugin, self).__init__(repo_path, repo_root, repo_temp)
        self.git_repo = None
        logger.debug("Initialsied GitLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def get_repo_load_path(self):
        """Get the path on disk to load the repository from.

        Returns:
            str: The path on disk to load the repository from.
        """
        return self.repo_temp

    def clone_repo(self):
        """Clone the Node Manager repository.

        Returns:
            git.Repo: The cloned repository.
        """
        cloned_repo = None
        try:
            cloned_repo = Repo(self.repo_root)
            cloned_repo.git.pull()
        except (NoSuchPathError, InvalidGitRepositoryError) as error:
            logger.debug(
                "Couldn't load repo from {path}, clone instead.".format(
                    path=self.repo_root,
                )
            )
            logger.debug(error)

        if not cloned_repo:
            cloned_repo = Repo.clone_from(self.repo_path, self.repo_root, depth=1)

        return cloned_repo

    def build_repo(self):
        """Build the Node Manager repository."""
        os.makedirs(self.repo_temp)
        expanded_hda_dir = os.path.join(self.repo_root, "dcc", "houdini", "hda")
        for hda in os.listdir(expanded_hda_dir):
            path = os.path.join(expanded_hda_dir, hda)
            hda_path = os.path.join(self.repo_temp, hda)
            logger.info("Processing {source}".format(source=path))
            hotl_cmd = ["hotl", "-C", path, hda_path]
            logger.debug(hotl_cmd)
            result = subprocess.call(hotl_cmd)
            if result != 0:
                raise RuntimeError(
                    "Failed to build HDA: {hda}".format(hda=hda)
                )

    def load(self):
        """Load the Node Manager repository."""
        self.git_repo = self.clone_repo()
        self.build_repo()
        return super(NodeManagerPlugin, self).load()
