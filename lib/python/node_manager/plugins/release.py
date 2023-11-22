#!/usr/bin/env python

"""Default Release Plugin."""

import logging
import os

import hou

from node_manager import utils
from node_manager.utils import definition as definition_utils
from node_manager.utils import nodes
from node_manager.utils import nodetypeutils

plugin_name = "DefaultRelease"
plugin_class = "release"
logger = logging.getLogger(
    "{plugin_class}.{plugin_name}".format(
        plugin_name=plugin_name,
        plugin_class=plugin_class,
    )
)


class NodeManagerPlugin(object):
    """Default Release Plugin."""
    name = plugin_name
    plugin_type = plugin_class

    def __init__(self):
        """Initialise the DefaultRelease plugin."""
        self.manager = utils.get_manager()
        self.repo = self.manager.get_release_repo()
        logger.debug("Initialise Release.")

    def get_release_definition(self, current_node):
        """Get the release definition for the given node.

        Args:
            current_node(hou.Node): The node to get the release definition for.

        Returns:
            hou.HDADefinition: The release definition.
        """
        definition = nodes.definition_from_node(current_node.path())
        definition.updateFromNode(current_node)
        return definition

    def release(self, current_node, release_comment=None):
        """Initialise Node Repositories from the NODE_MANAGER_REPOS environment
        variable.

        Args:
            current_node(hou.Node): The node to release.
            release_comment(str): The release comment.

        Returns:
            list: A list of Node Manager Repo objects.
        """
        logger.info("Beginning HDA release.")

        # Get the release definitionq
        definition = self.get_release_definition(current_node)

        node_file_path = definition.libraryFilePath()
        if not release_comment:
            release_comment = "Updated {name}".format(
                name=nodetypeutils.node_type_name(node_file_path)
            )

        logger.debug("Release comment: {comment}".format(comment=release_comment))

        logger.debug("Using release repo: {repo}".format(repo=self.repo.context.get("name")))
        logger.debug("Repo path: {path}".format(path=self.repo.context.get("repo_path")))

        # Expand the HDA ready for release
        hda_name = utils.expanded_hda_name(definition)
        release_path = os.path.join(self.repo.context.get("repo_path"), hda_name)
        logger.debug("Using release path: {path}".format(path=release_path))
        if os.path.isfile(release_path):
            logger.warning("Exisitng file will be overwritten by release to {path}".format(path=release_path))
            backup_directory = self.repo.get_repo_backup_dir()
            if not backup_directory:
                raise RuntimeError("No backup directory found for {repo}".format(repo=self.repo.context.get("name")))

            backup_path = os.path.join(backup_directory, os.path.basename(node_file_path))
            # This might cause issues if the file is already loaded by Houdini
            os.rename(release_path, backup_path)
            logger.warning("Previous file backed up to {path}".format(path=backup_path))
            
        definition.copyToHDAFile(release_path)
        logger.debug("Definition copied to {path}".format(path=release_path))

        # Add newly released .hda
        self.repo.process_node_definition_file(release_path, force=True)

        # Uninstall the old definition
        definition_utils.uninstall_definition(definition)

        # Success
        hou.ui.displayMessage(
            "HDA release successful!", title="HDA Manager: Publish HDA"
        )
        return True
