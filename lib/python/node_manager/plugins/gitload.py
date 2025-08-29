#!/usr/bin/env pythonß

"""Git Load plugin that will load node defintions stored in a Git repository."""

import logging
import os
import subprocess

import hou

from git import Repo
from git.exc import NoSuchPathError, InvalidGitRepositoryError

from node_manager.plugins import load

logger = logging.getLogger(__name__)


class NodeManagerPlugin(load.NodeManagerPlugin):
    name = "GitLoad"

    def __init__(self):
        """Initialise the GitLoad plugin."""
        super(NodeManagerPlugin, self).__init__()
        self.repo.context["git_repo_root"] = self.git_repo_root()
        self.repo.context["git_repo_clone"] = self.git_repo_clone_dir()
        self.repo.context["repo_load_path"] = self.repo_load_dir()
        self.repo.context["config_path"] = self.config_path()
        logger.info(f"Config path: {self.repo.context.get('config_path')}")
        logger.info(f"Exists: {os.path.isfile(self.repo.context.get('config_path'))}")
        logger.debug(
            "Initialise GitLoad: {repo_path}".format(
                repo_path=self.repo.context.get("repo_path"),
            )
        )

    def config_path(self):
        """Get the path to the config file.

        Returns:
            (str): The path to the config file.
        """
        return os.path.join(
            self.repo.context.get("git_repo_clone"),
            "config",
            "config.json",
        )

    def git_repo_root(self):
        """Get the git repo root directory.

        Returns:
            str: The path to the HDA repo on disk.
        """
        return os.path.join(
            self.manager.context.get("manager_temp_dir"), self.repo.context.get("repo_name")
        )

    def git_repo_clone_dir(self):
        """Get the git repo clone directory.

        Returns:
            str: The path to the HDA repo on disk.
        """
        return os.path.join(
            self.repo.context.get("git_repo_root"), "clone", self.repo.context.get("repo_name")
        )

    def repo_load_dir(self):
        """Get the repo load directory.

        Returns:
            str: The path to the HDA repo on disk.
        """
        return os.path.join(
            self.repo.context.get("git_repo_root"), "load", self.repo.context.get("repo_name")
        )

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
            cloned_repo = Repo.clone_from(
                self.repo.context.get("repo_path"), repo_root, depth=1
            )

        return cloned_repo

    def build_repo(self):
        """Build the Node Manager repository."""
        repo_root = self.repo.context.get("git_repo_clone")
        repo_build = self.repo.context.get("repo_load_path")
        if not os.path.exists(repo_build):
            os.makedirs(repo_build)
            logger.debug("Created temp directory: {path}".format(path=repo_build))
        expanded_hda_dir = os.path.join(repo_root, "dcc", "houdini", "hda")

        if not os.path.isdir(expanded_hda_dir):
            logger.warning(
                "Nothing to build, no HDA directory found: {path}".format(
                    path=expanded_hda_dir
                )
            )
            return

        for hda in os.listdir(expanded_hda_dir):
            path = os.path.join(expanded_hda_dir, hda)
            hda_path = os.path.join(repo_build, hda)
            logger.info("Processing {source}".format(source=path))
            hotl_cmd = [
                "hotl",
                "-c"
                if hou.isApprentice()
                else "-l",  # Maybe we should error-check this?
                path,
                hda_path,
            ]
            result = subprocess.call(hotl_cmd)
            if result != 0:
                raise RuntimeError("Failed to build HDA: {hda}".format(hda=hda))

    def load(self):
        """Load the Node Manager repository."""
        self.repo.context["git_repo"] = self.clone_repo()
        self.build_repo()
        return super(NodeManagerPlugin, self).load()
