#!/usr/bin/env python

import logging
import os

import hou

from node_manager import utils
from node_manager import utilities
from node_manager.dependencies import nodes

plugin_name = "DefaultRelease"
plugin_class = "release"
logger = logging.getLogger(
    "{plugin_class}.{plugin_name}".format(
        plugin_name=plugin_name,
        plugin_class=plugin_class,
    )
)


class NodeManagerPlugin(object):
    name = plugin_name
    plugin_type = plugin_class

    def __init__(self):
        """ 
        """
        self.manager = utils.get_manager()
        logger.debug("Initialise Release.")

    def get_release_repo(self, definition):
        """Get the release repository for the given definition.

        Args:
            definition(hou.HDADefinition): The definition to get the release
                repository for.

        Returns:
            object: The release repository.
        """
        # Here we will need to get the actual repo that should be used for the given
        # definition. For now we will cheat and just use the first repo.
        for node_repo in self.manager.node_repos:
            return self.manager.node_repos.get(node_repo)

        raise RuntimeError("No release repository found.")

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

        definition = nodes.definition_from_node(current_node.path())
        definition.updateFromNode(current_node)

        node_file_path = definition.libraryFilePath()
        if not release_comment:
            release_comment = "Updated {name}".format(
                name=utilities.node_type_name(node_file_path)
            )

        logger.debug("Release comment: {comment}".format(comment=release_comment))

        repo = self.get_release_repo(definition)
        logger.debug("Using release repo: {repo}".format(repo=repo.name))
        logger.debug("Repo path: {path}".format(path=repo.repo_path))

        # Expand the HDA ready for release
        hda_name = utilities.expanded_hda_name(definition)
        release_path = os.path.join(repo.repo_path, hda_name)
        logger.debug("Using release path: {path}".format(path=release_path))
        if os.path.isfile(release_path):
            logger.warning("Exisitng file will be overwritten by release to {path}".format(path=release_path))
            backup_directory = repo.get_repo_backup_dir()
            if not backup_directory:
                raise RuntimeError("No backup directory found for {repo}".format(repo=repo.name))

            backup_path = os.path.join(backup_directory, os.path.basename(node_file_path))
            # This might cause issues if the file is already loaded by Houdini
            os.rename(release_path, backup_path)
            logger.warning("Previous file backed up to {path}".format(path=backup_path))
            
        definition.copyToHDAFile(release_path)
        logger.debug("Definition copied to {path}".format(path=release_path))

        # Add newly released .hda
        repo.process_node_definition_file(release_path, force=True)

        # Remove released definition
        repo.remove_definition(definition)

        # Success
        hou.ui.displayMessage(
            "HDA release successful!", title="HDA Manager: Publish HDA"
        )
