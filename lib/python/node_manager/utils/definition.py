#!/usr/bin/env python

"""Node manager utils."""

import logging
import os
import shutil

import hou


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
