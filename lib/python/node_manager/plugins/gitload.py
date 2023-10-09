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

    def __init__(self, repo):
        """Initialise the GitLoad plugin."""
        super(NodeManagerPlugin, self).__init__(repo)
        self.repo.context["git_repo_root"] = self.git_repo_root()
        self.repo.context["git_repo_temp"] = self.git_repo_temp()
        logger.debug("Initialsied GitLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    # def get_repo_load_path(self):
    #     """Get the path on disk to load the repository from.

    #     Returns:
    #         str: The path on disk to load the repository from.
    #     """
    #     return self.repo_temp

    def git_repo_root(self):
        """Get the git repo root directory.

        Returns:
            str: The path to the HDA repo on disk."""
        return os.path.join(self.manager.context.get("manager_base_dir"), self.name)

    def git_repo_temp(self):
        """Get the temp directory for the HDA repo.

        Returns:
            str: The path to the HDA repo on disk."""
        return os.path.join(self.manager.context.get("manager_temp_dir"), self.name)

    def clone_repo(self):
        """Clone the Node Manager repository.

        Returns:
            git.Repo: The cloned repository.
        """
        cloned_repo = None
        repo_root = self.repo.context.get("git_repo_root")
        try:
            cloned_repo = Repo(repo_root)
            cloned_repo.git.pull()
        except (NoSuchPathError, InvalidGitRepositoryError) as error:
            logger.debug(
                "Couldn't load repo from {path}, clone instead.".format(
                    path=repo_root,
                )
            )
            logger.debug(error)

        if not cloned_repo:
            cloned_repo = Repo.clone_from(self.get_repo_load_path(), repo_root, depth=1)

        return cloned_repo

    def build_repo(self):
        """Build the Node Manager repository."""
        repo_root = self.repo.context.get("git_repo_root")
        repo_temp = self.repo.context.get("git_repo_temp")
        if not os.path.exists(repo_temp):
            os.makedirs(repo_temp)
            logger.debug("Created temp directory: {path}".format(path=repo_temp))
        expanded_hda_dir = os.path.join(repo_root, "dcc", "houdini", "hda")

        for hda in os.listdir(expanded_hda_dir):
            path = os.path.join(expanded_hda_dir, hda)
            hda_path = os.path.join(repo_temp, hda)
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
        self.repo.context["git_repo"] = self.clone_repo()
        self.build_repo()
        return super(NodeManagerPlugin, self).load()
