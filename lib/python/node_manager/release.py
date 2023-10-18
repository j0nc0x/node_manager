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
        repo,
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
        self.repo = repo
        logger.info("Initialised HDA Release process")
        logger.debug("Release directory: {path}".format(path=self.release_dir))

    def git_repo(self):
        return self.repo.context.get("git_repo")

    def git_dir(self):
        """
        Get the path to the git repository.

        Returns:
            (str): The path to the git repository.
        """
        logger.debug(self.repo)
        logger.debug(self.repo.context)
        logger.debug(self.repo.context.get("git_repo_clone"))
        return self.repo.context.get("git_repo_clone")

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

    def generate_release_version(self, version, major, minor, patch):
        """
        """
        if major + minor + patch != 1:
            raise RuntimeError("Invalid version increment.")

        release_version = None
        parsed_version = parse(version)
        if patch:
            release_version = "{major}.{minor}.{patch}".format(
                major=parsed_version.major,
                minor=parsed_version.minor,
                patch=parsed_version.micro + 1,
            )
        elif minor:
            release_version = "{major}.{minor}.{patch}".format(
                major=parsed_version.major,
                minor=parsed_version.minor + 1,
                patch=0,
            )
        elif major:
            release_version = "{major}.{minor}.{patch}".format(
                major=parsed_version.major + 1,
                minor=0,
                patch=0,
            )

        return release_version

    def get_release_version(self, conf_version, major, minor, patch, release_tags):
        """
        """
        limit = 10
        i = 0
        release_version = self.generate_release_version(conf_version, major, minor, patch)
        while release_version in release_tags:
            i += 1
            release_version = self.generate_release_version(release_version, major, minor, patch)

            if i > limit:
                raise RuntimeError("Failed to generate release version after {iteration} iterations.".format(iteration=i))

        if i:
            logger.warning("Release version took {iteration} iterations to generate.".format(iteration=i + 1))

        return release_version

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

        # Create the branch
        current = self.git_repo().create_head(self.release_branch)
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

        repo_conf_data = {}
        with open(config_path, "r") as repo_conf:
            repo_conf_data = json.load(repo_conf)

        # Get the release version
        release_tags = [str(tag) for tag in self.git_repo().tags]
        self.release_version = self.get_release_version(repo_conf_data.get("version"), major, minor, patch, release_tags)

        # Copy the expanaded HDA into it's correct location
        shutil.copytree(self.expand_dir(), hda_path)

        # See if anything was updated
        changes = [change.a_path for change in self.git_repo().index.diff(None)]
        if not changes and not self.git_repo().untracked_files:
            logger.debug("No changes have been made to this HDA, aborting.")
            return None

        # Add and commit
        self.git_repo().git.add(A=True)
        self.git_repo().git.commit(m=self.comment)
        self.git_repo().git.push("--set-upstream", "origin", current)

        # Increment version in config
        repo_conf_data["version"] = self.release_version
        with open(config_path, "w") as repo_conf:
            json.dump(repo_conf_data, repo_conf)

        # Commit and push
        self.git_repo().git.commit(config_path, m="Version up")
        self.git_repo().git.push()

        # Push tag to repo
        new_tag = self.git_repo().create_tag(self.release_version, message="Release {version}".format(version=self.release_version))
        self.git_repo().remotes.origin.push(new_tag)

        # merge to master
        self.git_repo().git.reset("--hard")
        main = self.git_repo().heads.main
        main.checkout()
        self.git_repo().git.pull()
        self.git_repo().git.merge(current, "--no-ff")
        self.git_repo().git.push()

        # remove release branch
        remote = self.git_repo().remote(name='origin')
        remote.push(refspec=(':{branch}'.format(branch=self.release_branch)))

        # clean up release dir
        #shutil.rmtree(self.release_dir)
        logger.debug(
            "(Would clean) up release directory {path}".format(path=self.release_dir)
        )

        # success
        logger.info("Release successful for {hda}.".format(hda=self.node_name))

        return True
