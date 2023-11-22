#!/usr/bin/env python

"""Edit the node definition in a separate edit directory."""

import logging
import os

from packaging.version import parse

import hou

from node_manager import utils
from node_manager.utils import definitionutils
from node_manager.utils import nodeutils

logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    """Default Edit Plugin."""

    name = "DefaultEdit"
    plugin_type = "edit"

    def __init__(self):
        """Initialise the plugin."""
        self.manager = utils.get_manager()

        logger.debug(
            "Initialise DefaultEdit."
        )

    def edit_definition(self, current_node, major=False, minor=False):
        """Edit the definition of the given node.

        Args:
            current_node(hou.Node): The node to edit.
            major(bool): Whether to increment the major version.
            minor(bool): Whether to increment the minor version.
        """
        logger.debug(
            "Edit {node} (Major: {major}, Minor: {minor})".format(
                node=current_node,
                major=major,
                minor=minor,
            )
        )
        definition = nodeutils.definition_from_node(current_node.path())

        dialog_message = (
            "You are about to edit a hda that is not the lastest version, do "
            "you want to continue?"
        )

        if not self.manager.is_latest_version(current_node) and utils.display_message(
            dialog_message, ("Ok", "Cancel"), title="Warning"
        ):
            logger.info("Making definition editable aborted by user.")
            return

        new_version = None
        if major or minor:
            logger.debug("Major or Minor version updated for editable node.")
            current_version = utils.node_type_version(definition.nodeTypeName())
            logger.debug(
                "Current version is {version}".format(version=current_version)
            )
            current_version_components = len(current_version.split("."))
            logger.debug(
                "Current version has {components} components".format(
                    components=current_version_components,
                )
            )
            version = parse(current_version)
            new_version = "{major}.{minor}".format(
                major=version.major + major,
                minor=0 if major else version.minor + minor,
            )
            logger.debug(
                "New version will be {version}".format(
                    version=new_version,
                )
            )
            if current_version_components == 3:
                logger.debug(
                    "Current version is major.minor.patch, adding patch."
                )
                new_version = "{new_version}.{micro}".format(
                    new_version=new_version,
                    micro=version.micro,
                )

            logger.debug(
                "Editable node will be created with new version {version}".format(
                    version=new_version,
                )
            )

        # First determine if we can work where the node is currently located
        manager_node = self.manager.is_node_manager_node(current_node)
        node_editable = os.access(definition.libraryFilePath(), os.W_OK)
        directory_editable = os.access(os.path.dirname(definition.libraryFilePath()), os.W_OK)
        if manager_node == False and node_editable == True and directory_editable == True:
            # We can edit this definition in its current location, no need to make a copy
            logger.info("Node editable in its current location on disk.")
            edit_directory = os.path.dirname(definition.libraryFilePath())
        else:
            edit_directory = self.manager.context.get("manager_edit_dir")

        # Copy and install definition modifying the nodetypename
        updated_node_type_name = definitionutils.create_definition_copy(
            definition,
            edit_directory,
            version=new_version,
        )
        logger.debug(
            "Updated node type name: {name}".format(
                name=updated_node_type_name,
            )
        )

        if updated_node_type_name:
            # Update the node in the scene
            logger.debug(
                "Updating {node} to {name}".format(
                    node=current_node,
                    name=updated_node_type_name,
                )
            )
            current_node.changeNodeType(updated_node_type_name)

        # Clean up the old definition  if it wasn't part of repo
        definition_path = definition.libraryFilePath()
        repo = self.manager.repo_from_hda_file(definition_path)
        if not repo:
            logger.debug("Unistalling {path}".format(path=definition_path))
            hou.hda.uninstallFile(definition.libraryFilePath())
