#!/usr/bin/env python

"""HDA manager release process."""

import json
import logging
import os
import re
import shutil

from packaging.version import parse

from git import Repo

from node_manager import utilities

logger = logging.getLogger(__name__)


class HDARelease(object):
    """The HDA Release process.

    This class handles the release process for a hou.HDADefinition that is ready to be
    published. We ultimately want to have the option to run this outside of Houdini -
    ie. on a server, so also want to avoid taking up a Houdini Engine license / running
    the risk of not getting a license. Therefore all Houdini operations are complete
    prior to this class being initialised.
    """

    # __config = get_config()
    # hda_repo = __config.get("hda_repo")
    hda_repo = "git@github.com:j0nc0x/hda_repo.git" # Read this from repo config to allow multiple git repositories
    # package_root = "/Users/jcox/source/hda_library" # Read this from repo config to allow multiple git repositories

    def __init__(
        self,
        release_dir,
        node_type_name,
        release_branch,
        node_name,
        package,
        release_comment,
    ):
        """
        Initialise HDARelease to prepare the release process.

        Args:
            release_dir(str): The working directory where the release will be run.
            node_type_name(str): The node type name of the HDA being released.
            release_branch(str): The branch to use for the release.
            node_name(str): The name of the node being released.
            package(str): The name of the package being released.
            release_comment(str): The comment to use for the release.
        """
        self.release_dir = release_dir
        self.node_type_name = node_type_name
        self.release_branch = release_branch
        self.node_name = node_name
        self.release_version = None
        self.package = package
        self.comment = release_comment
        logger.info("Initialised HDA Release process")

    def git_dir(self):
        """
        Get the path to the git repository.

        Returns:
            (str): The path to the git repository.
        """
        return os.path.join(self.release_dir, "git")

    def expand_dir(self):
        """
        Get the path where the HDA will be expanded.

        Returns:
            (str): The HDA expand directory.
        """
        return os.path.join(self.release_dir, self.node_name)

    def node_root(self):
        """
        """
        return os.path.join(self.git_dir(), "dcc", "houdini", "hda")

    def node_path(self):
        """
        Get the path to the node to be released.

        Returns:
            (str): The node path.
        """
        return os.path.join(self.node_root(), self.node_name)

    def config_path(self):
        """
        """
        return os.path.join(self.git_dir(), "config", "config.json")

    def release(self):
        """
        Run the HDA release process.

        Returns:
            (str): The path of the released HDA.

        Raises:
            RuntimeError: The rez package released wasn't successful.
        """
        patch = False
        minor = False
        major = False

        config_path = self.config_path()

        # Clone the repo
        cloned_repo = Repo.clone_from(self.hda_repo, self.git_dir())

        current = cloned_repo.create_head(self.release_branch)
        current.checkout()

        # Check if expanded node directory already exists, delete it if it does
        hda_path = self.node_path()
        if os.path.exists(hda_path):
            patch = True
            shutil.rmtree(hda_path)
            logger.debug(
                "Removed directory already exists, removing: {path}".format(
                    path=hda_path
                )
            )
        else:
            namespace = utilities.node_type_namespace(self.node_type_name)
            name = utilities.node_type_name(self.node_type_name)
            version = utilities.node_type_version(self.node_type_name)
            regex = re.compile(".*{namespace}\.{name}\.{major}\.(\d*).hda".format(namespace=namespace, name=name, major=parse(version).major))
            same_major_version = [path for path in os.listdir(self.node_root()) if regex.match(path)]
            if same_major_version:
                minor = True
            else:
                major = True

        # Copy the expanaded HDA into it's correct location
        shutil.copytree(self.expand_dir(), hda_path)

        # See if anything was updated
        changes = [change.a_path for change in cloned_repo.index.diff(None)]
        if not changes and not cloned_repo.untracked_files:
            logger.debug("No changes have been made to this HDA, aborting.")
            return None

        # Add and commit
        cloned_repo.git.add(A=True)
        cloned_repo.git.commit(m=self.comment)
        cloned_repo.git.push("--set-upstream", "origin", current)

        repo_conf_data = {}
        with open(config_path, "r") as repo_conf:
            repo_conf_data = json.load(repo_conf)

        if major + minor + patch != 1:
            raise RuntimeError("Invalid version increment.")     

        version = parse(repo_conf_data.get("version"))
        if patch:
            self.release_version = "{major}.{minor}.{patch}".format(
                major=version.major,
                minor=version.minor,
                patch=version.micro + 1,
            )
        elif minor:
            self.release_version = "{major}.{minor}.{patch}".format(
                major=version.major,
                minor=version.minor + 1,
                patch=0,
            )
        elif major:
            self.release_version = "{major}.{minor}.{patch}".format(
                major=version.major + 1,
                minor=0,
                patch=0,
            )

        repo_conf_data["version"] = self.release_version

        with open(config_path, "w") as repo_conf:
            json.dump(repo_conf_data, repo_conf)

        # Commit and push
        cloned_repo.git.commit(config_path, m="Version up")
        cloned_repo.git.push()

        # Push tag to repo
        new_tag = cloned_repo.create_tag(self.release_version, message="Release {version}".format(version=self.release_version))
        cloned_repo.remotes.origin.push(new_tag)

        # merge to master
        cloned_repo.git.reset("--hard")
        main = cloned_repo.heads.main
        main.checkout()
        cloned_repo.git.pull()
        cloned_repo.git.merge(current, "--no-ff")
        cloned_repo.git.push()

        # clean up release dir
        #shutil.rmtree(self.release_dir)
        logger.debug(
            "(Would clean) up release directory {path}".format(path=self.release_dir)
        )

        # success
        logger.info("Release successful for {hda}.".format(hda=self.node_name))

        return True
