#!/usr/bin/env python

"""Git Release Plugin that will release a node definition in expaned form to Git source control."""

import json
import logging
import os
import re
import shutil
import subprocess
import time

import hou

from node_manager import utils
from node_manager.utils import nodetypeutils
from node_manager.plugins import release

plugin_name = "GitRelease"
plugin_class = "release"
logger = logging.getLogger(
    "{plugin_class}.{plugin_name}".format(
        plugin_name=plugin_name,
        plugin_class=plugin_class,
    )
)


class NodeManagerPlugin(release.NodeManagerPlugin):
    """Git Release Plugin."""

    name = plugin_name
    plugin_type = plugin_class

    def __init__(self):
        """Initialise the GitRelease plugin."""
        super(NodeManagerPlugin, self).__init__()

        self._release_dir = None
        self._node_type_name = None
        self.node_name = None

        logger.debug("Initialise Release.")

    def package_name(self):
        """
        Lookup the package name from the context.

        Returns:
            (str): The package name.
        """
        if self.repo:
            return self.repo.context.get("repo_name")
        return None

    def release_dir(self):
        """
        Get the path to the HDA edit release directory.

        Returns:
            (str): The release directory.
        """
        return os.path.join(self.repo.context.get("git_repo_root"), "release")

    def _git_repo(self):
        """Get the git repository.

        Returns:
            (git.Repo): The git repository.
        """
        return self.repo.context.get("git_repo")

    def _git_dir(self):
        """
        Get the path to the git repository.

        Returns:
            (str): The path to the git repository.
        """
        return self.repo.context.get("git_repo_clone")

    def _expand_dir(self):
        """
        Get the path where the HDA will be expanded.

        Returns:
            (str): The HDA expand directory.
        """
        return os.path.join(self._release_dir, self.node_name)

    def _node_root(self):
        """Get the path to the node root.

        Returns:
            (str): The path to the node root.
        """
        return os.path.join(self._git_dir(), "dcc", "houdini", "hda")

    def _node_path(self):
        """
        Get the path to the node to be released.

        Returns:
            (str): The node path.
        """
        return os.path.join(self._node_root(), self.node_name)

    def _config_path(self):
        """Get the path to the config file.

        Returns:
            (str): The path to the config file.
        """
        return os.path.join(self._git_dir(), "config", "config.json")

    def process_release(self, definition, branch, comment=None):
        """
        Run the HDA release process.

        Args:
            definition(hou.HDADefinition): The definition to release.
            branch(str): The name of the branch to release to.
            comment(str, optional): The comment to use for the release.

        Returns:
            (str): The path of the released HDA.

        Raises:
            RuntimeError: The rez package released wasn't successful.
        """
        config_path = self._config_path()

        # Create the branch
        current = self._git_repo().create_head(branch)
        current.checkout()

        # # Check if expanded node directory already exists, delete it if it does
        hda_path = self._node_path()
        if os.path.exists(hda_path):
            shutil.rmtree(hda_path)
            logger.debug(
                "Removed directory already exists, removing: {path}".format(
                    path=hda_path
                )
            )

        repo_conf_data = {}
        if os.path.isfile(config_path):
            with open(config_path, "r") as repo_conf:
                repo_conf_data = json.load(repo_conf)
        else:
            logger.warning(
                "No config found at {path}, skipping.".format(path=config_path)
            )

        # Get the release version
        self.release_version = self.manager.get_release_version(
            definition, repo_conf_data.get("version", "0.0.0")
        )

        # Copy the expanaded HDA into it's correct location
        shutil.copytree(self._expand_dir(), hda_path)

        # See if anything was updated
        changes = [change.a_path for change in self._git_repo().index.diff(None)]
        if not changes and not self._git_repo().untracked_files:
            logger.debug("No changes have been made to this HDA, aborting.")
            return None

        # Add and commit
        self._git_repo().git.add(A=True)
        self._git_repo().git.commit(m=comment)
        self._git_repo().git.push("--set-upstream", "origin", current)

        # Update the docs
        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.info(os.listdir(hda_path))
        logger.info(self._node_type_name)
        definition_subdirectory = nodetypeutils.definition_subdir(
            self._node_type_name,
            definition.nodeTypeCategory().name(),
        )

        # Node Icon
        icon_path = os.path.join(hda_path, definition_subdirectory, "IconSVG")
        has_icon = False
        logger.info("Icon sub-directory: {path}".format(path=icon_path))
        if os.path.isfile(icon_path):
            logger.info("Icon file found at {path}".format(path=icon_path))
            has_icon = True

        # Node Description
        description_path = os.path.join(hda_path, definition_subdirectory, "Description")
        has_description = False
        logger.info("Description sub-directory: {path}".format(path=description_path))
        if os.path.isfile(description_path):
            logger.info("Description file found at {path}".format(path=description_path))
            has_description = True

        # Parm Help
        parm_templates_group = definition.parmTemplateGroup()
        parm_help = []
        if parm_templates_group:
            for parm_template in parm_templates_group.parmTemplates():
                logger.info(parm_template)
                parm_help.append(
                    {
                        "name": parm_template.name(),
                        "help": parm_template.help(),
                    }
                )
        if parm_help:
            logger.info("Parm help found: {help}".format(help=parm_help))

        # Increment version in config
        repo_conf_data["version"] = self.release_version
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as repo_conf:
            json.dump(repo_conf_data, repo_conf)

        # Commit and push
        self._git_repo().git.add(A=True)
        self._git_repo().git.commit(config_path, m="Version up")
        self._git_repo().git.push()

        # Push tag to repo
        new_tag = self._git_repo().create_tag(
            self.release_version,
            message="Release {version}".format(version=self.release_version),
        )
        self._git_repo().remotes.origin.push(new_tag)

        # merge to master
        self._git_repo().git.reset("--hard")
        main = self._git_repo().heads.main
        main.checkout()
        self._git_repo().git.pull()
        self._git_repo().git.merge(current, "--no-ff")
        self._git_repo().git.push()

        # remove release branch
        remote = self._git_repo().remote(name="origin")
        remote.push(refspec=(":{branch}".format(branch=branch)))

        # clean up release dir
        # shutil.rmtree(self._release_dir)
        logger.debug(
            "(Would clean) up release directory {path}".format(path=self._release_dir)
        )

        # success
        logger.info("Release successful for {hda}.".format(hda=self.node_name))

        return True

    def release(self, current_node, release_comment=None):
        """
        Publish a definition being edited by the Node manager.

        Args:
            current_node(hou.Node): The node to publish the definition for.
            release_comment(str, optional): The comment to use for the release.

        Raises:
            RuntimeError: HDA couldn't be expanded or package couldn't be found.

        Returns:
            bool: Was the release successful.
        """
        logger.info("Beginning HDA release.")

        # Get the release definitionq
        definition = self.get_release_definition(current_node)

        node_file_path = definition.libraryFilePath()
        if not release_comment:
            release_comment = "Updated {name}".format(
                name=nodetypeutils.node_type_name(node_file_path)
            )

        # Define the release directory
        release_subdir = "release_{time}".format(time=int(time.time()))
        full_release_dir = os.path.join(self.release_dir(), release_subdir)

        # Expand the HDA ready for release
        hda_name = utils.expanded_hda_name(definition)
        expand_dir = os.path.join(full_release_dir, hda_name)

        # expandToDirectory doesn't allow inclusion of contents - raise with SideFx, but
        # reverting to subprocess.
        cmd = [
            "hotl",
            "-x" if hou.isApprentice() else "-tp",  # Maybe we should error-check this?
            expand_dir,
            definition.libraryFilePath(),
        ]
        process = subprocess.Popen(cmd)
        process.wait()

        # verify release
        if process.returncode != 0:
            # Non-zero return code
            raise RuntimeError("HDA expansion didn't complete successfully.")

        # Determine the other information needed to conduct a release
        node_type_name = definition.nodeTypeName()
        branch = utils.release_branch_name(definition)
        package = self.package_name()
        if not package:
            raise RuntimeError("No package found for definition")

        self._release_dir = full_release_dir
        self._node_type_name = node_type_name
        self.node_name = hda_name

        return self.process_release(definition, branch, comment=release_comment)
