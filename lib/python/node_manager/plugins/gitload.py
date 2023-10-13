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
        self.repo.context["git_repo_clone"] = self.git_repo_clone_dir()
        self.repo.context["repo_load_path"] = os.path.join(
            self.manager.context.get("manager_temp_dir"),
            self.repo.context.get("name"),
        )
        logger.debug(
            "Initialise GitLoad: {repo_path}".format(
                repo_path=self.repo.context.get("repo_path"),
            )
        )

    def git_repo_root(self):
        """Get the git repo root directory.

        Returns:
            str: The path to the HDA repo on disk."""
        return os.path.join(self.manager.context.get("manager_base_dir"), self.repo.context.get("name"))

    def git_repo_clone_dir(self):
        """Get the git repo clone directory.

        Returns:
            str: The path to the HDA repo on disk."""
        return os.path.join(self.repo.context.get("git_repo_root"), self.repo.context.get("name"))

    def clone_repo(self):
        """Clone the Node Manager repository.

        Returns:
            git.Repo: The cloned repository.
        """
        cloned_repo = None
        repo_root = self.repo.context.get("git_repo_clone")
        try:
            cloned_repo = Repo(repo_root)
            cloned_repo.git.pull()
            logger.debug("Loaded repo from {path}".format(path=repo_root))
        except (NoSuchPathError, InvalidGitRepositoryError) as error:
            logger.debug("Couldn't load repo from {path}".format(path=repo_root))

        if not cloned_repo:
            logger.debug(
                "Couldn't load repo from {path}, clone instead.".format(
                    path=repo_root,
                )
            )
            if not os.path.isdir(repo_root):
                os.makedirs(repo_root)
                logger.debug("Created repo directory: {path}".format(path=repo_root))
            cloned_repo = Repo.clone_from(self.repo.context.get("repo_path"), repo_root, depth=1)

        return cloned_repo

    def build_repo(self):
        """Build the Node Manager repository."""
        repo_root = self.repo.context.get("git_repo_clone")
        repo_build = self.repo.context.get("repo_load_path")
        logger.debug("-----")
        logger.debug("Repo root: {path}".format(path=repo_root))
        logger.debug("Repo build: {path}".format(path=repo_build))
        logger.debug("-----")
        if not os.path.exists(repo_build):
            os.makedirs(repo_build)
            logger.debug("Created temp directory: {path}".format(path=repo_build))
        expanded_hda_dir = os.path.join(repo_root, "dcc", "houdini", "hda")

        for hda in os.listdir(expanded_hda_dir):
            path = os.path.join(expanded_hda_dir, hda)
            hda_path = os.path.join(repo_build, hda)
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
