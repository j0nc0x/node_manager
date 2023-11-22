#!/usr/bin/env python

"""Node manager utils."""

import logging
import os
import shutil

import hou

from node_manager import utils
from node_manager.utils import nodetypeutils


logger = logging.getLogger(__name__)


def embedded_definition(definition):
    """
    Determine if the given hou.HDADefinition is embedded.

    Args:
        definition(hou.HDADefinition): The definition to check.

    Returns:
        (bool): Is the definition embedded.
    """
    if definition.libraryFilePath() == "Embedded":
        return True

    return False


def uninstall_definition(definition, backup_dir=None):
    """Uninistall the given definition from the current Houdini session.

    If a backup directory has been provided, also move the .hda file to backup.

    Args:
        definition(hou.HDADefinition): The HDA definition to uninstall.
        backup_dir(:obj:`str`,optional): The backup directoruy to keep a backup in
            before uninstalling.
    """
    # NOTE: Maybe error check here whether the node is a Node Manager node or not?

    # Uninstall the definition
    path = definition.libraryFilePath()
    hou.hda.uninstallFile(path)

    # Move the .hda file to backup
    if backup_dir:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        shutil.move(path, backup_dir)
        logger.debug(
            "{path} backed-up to {backup}.".format(
                path=os.path.basename(path), backup=backup_dir
            )
        )


def cleanup_embedded_definitions(nodetype):
    """
    Cleanup any embedded definition found for the given nodetype.

    Args:
        nodetype(hou.NodeType): The nodetype to clean-up any embedded defintions for.
    """
    for definition in nodetype.allInstalledDefinitions():
        if embedded_definition(definition) and not definition.isCurrent():
            definition.destroy()
            logger.debug(
                "Embedded definition removed for {name}.".format(
                    name=nodetype.name(),
                )
            )


def create_definition_copy(definition, edit_dir, namespace=None, name=None, version=None):
    """Create a copy of a node definition.

    Update the nodeTypeName if required.

    Args:
        definition(hou.HDADefinition): The node definition to copy.
        namespace(:obj:`str`,optional): The node namespace to use for the copy.
        name(:obj:`str`,optional): The node name to use for the copy.
        version(:obj:`str`,optional): The node version to use for the copy.

    Returns:
        (str): The name of the copied node.
    """
    logger.debug(
        "Creating copy of definition {definition}".format(
            definition=definition.nodeTypeName(),
        )
    )
    logger.debug(
        "Updating namespace: {namespace}, name: {name}, version: {version}".format(
            namespace=namespace,
            name=name,
            version=version,
        )
    )
    # Write the HDA to the edit_dir
    editable_path = utils.editable_hda_path_from_components(
        definition,
        edit_dir,
        namespace=namespace,
        name=name,
    )
    logger.debug("Editable path: {path}".format(path=editable_path))

    # See if we are updating the NodeTypeName
    if namespace or name or version:
        new_name = nodetypeutils.node_type_name_from_components(
            definition, namespace=namespace, name=name, version=version
        )
        logger.debug("Using new name: {new_name}".format(new_name=new_name))
    else:
        new_name = None

    definition.copyToHDAFile(editable_path, new_name=new_name)
    logger.debug("Definition saved to {path}".format(path=editable_path))

    # Install the newly written HDA
    hou.hda.installFile(
        editable_path,
        oplibraries_file="Scanned Asset Library Directories",
        force_use_assets=True,
    )

    return new_name
