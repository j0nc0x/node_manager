#!/usr/bin/env python

"""Node manager utils."""

import logging
import os
import time

import hou

from node_manager import manager
from node_manager.utils import nodetypeutils


logger = logging.getLogger(__name__)


def get_manager():
    """Get the node manager instance if one exists.

    Returns:
        node_manager.NodeManager: The current instance of Node Manager.

    Raises:
        RuntimeError: Node Manager not initialised.
    """
    manager_instance = manager.NodeManager.instance
    if not manager_instance:
        logger.warning("Node Manager not initialised.")
    return manager_instance


def display_message(
    text,
    buttons=("OK",),
    severity=hou.severityType.Message,
    default_choice=0,
    close_choice=-1,
    help=None,
    title=None,
    details=None,
    details_label=None,
    details_expanded=False,
):
    """Display a Houdini message UI element if we are in GUI mode.

    Also output to the logger, with the logging type specified by the severity.

    Args:
        text(str): The message to display.
        buttons(tuple): A sequence of strings containing the names of the
            buttons. By default the message window contains a single OK button.
        severity(hou.severityType): A hou.severityType value that determines
            which icon to display on the dialog. Note that using
            hou.severityType.Fatal will exit Houdini after the user closes the
            dialog.
        default_choice(int): The index of the button that is selected if the
            user presses enter.
        close_choice(int): The index of the button that is selected if the user
            presses Escape or closes the dialog.
        help(str): Additional help information to display below the main
            message.
        title(str): The window's title. If None, the title is "Houdini".
        details(str): A string containing extra messages that is not visible
            unless the user clicks "Show Details".
        details_label(str): A string containing the label for the
            expand/collapse button that controls whether or not the detail text
            is visible. If details_expanded is set to true this parameter has
            no effect.
        details_expanded(bool): A boolean, if true then the text area where the
            detail messages appear is always shown and cannot be collapsed. If
            false, the detail message area is initially folded when the message
            box is popped up and the user can expand to read the details.

    Returns:
        result(int): The index of the button the user pressed.
    """
    # Always log the message a line at a time
    text_split = text.split("\n")
    for line in text_split:
        if line == "":
            continue

        if severity == hou.severityType.Error or severity == hou.severityType.Fatal:
            logger.error(line)
        elif severity == hou.severityType.Warning:
            logger.warning(line)
        else:
            logger.info(line)

    result = None

    # Display the Houdini UI message if the dialog is available
    if hou.isUIAvailable():
        result = hou.ui.displayMessage(
            text,
            buttons=buttons,
            severity=severity,
            default_choice=default_choice,
            close_choice=close_choice,
            help=help,
            title=title,
            details=details,
            details_label=details_label,
            details_expanded=details_expanded,
        )
    return result


def node_type_index(node_type_name, category):
    """Generate a node type index.

    We use namespace::category/name as our index for our NodeTypes stored in the
    manager. Use the given hou.HDADefinition to generate an index.

    Args:
        node_type_name(str): The full node type name to lookup against.
        category(str): The node type category to lookup against.

    Returns:
        index(str): The node type index based on the given criteria.
    """
    index = None
    if nodetypeutils.valid_node_type_name(node_type_name):
        name_sections = nodetypeutils.node_type_name_components(node_type_name)
        name_sections[-2] = "{category}/{name}".format(
            category=category, name=name_sections[-2]
        )
        index = "::".join(name_sections[:-1])

    return index


def release_branch_name(definition):
    """
    Generate a legal git release branch name for the given definition.

    Args:
        definition(hou.HDADefinition): The HDA definition to get the release branch for.

    Returns:
        (str): The git release branch for the given definition.
    """
    category = definition.nodeTypeCategory().name()
    current_name = definition.nodeTypeName()
    namespace = nodetypeutils.node_type_namespace(current_name)
    name = nodetypeutils.node_type_name(current_name)
    version = nodetypeutils.node_type_version(current_name)
    ts = time.gmtime()
    release_time = time.strftime("%d-%m-%y-%H-%M-%S", ts)
    return "release_{category}-{namespace}{name}-{version}-{time}".format(
        category=category,
        namespace="{namespace}-".format(namespace=namespace) if namespace else "",
        name=name,
        version=version,
        time=release_time,
    )


def editable_hda_path_from_components(definition, edit_dir, namespace=None, name=None):
    """Get the editable HDA path.

    Generate a file path where a hou.HDADefinition can be edited within the given edit
    directory. If a new nodeType namespace or name has been provided take it into
    account when generating the path.

    Args:
        definition(hou.HDADefinition): The HDA definition to generate the editable HDA
            path for.
        edit_dir(str): The root edit directory.
        namespace(str): The updated namespace to use if it is being changed.
        name(str): The updated name to use if it is being changed.

    Returns:
        (str): The editable HDA path on disk.
    """
    category = definition.nodeTypeCategory()
    current_name = definition.nodeTypeName()
    if nodetypeutils.valid_node_type_name(current_name):
        # If the name is valid, use it
        logger.debug("Using valid node type name: %s", current_name)
        new_namespace = nodetypeutils.node_type_namespace(current_name, new_namespace=namespace)
        new_name = nodetypeutils.node_type_name(current_name, new_name=name)
        full_name = "{namespace}{name}".format(
            namespace="{namespace}_".format(namespace=new_namespace) if new_namespace else "",
            name=new_name,
        )
    else:
        # Otherwise just make do with whatever we have
        logger.debug("Using invalid node type name: %s", current_name)
        full_name = definition.nodeType().nameComponents()[2]

    editable_name = "{category}_{full_name}.{time}.hda".format(
        category=category.name(), full_name=full_name, time=int(time.time())
    )

    logger.debug("Editable name: %s", editable_name)
    logger.debug("Edit dir: %s", edit_dir)

    return os.path.join(edit_dir, editable_name)


def expanded_hda_name(definition):
    """Get the expanded HDA name.

    This function is used by the HDA manager to set the name of the directory a
    hou.HDADefinition is expanded to
    hou.nodeTypeCategory.name()_hou.nodeTypeName(namespace)_hou.nodeTypeName(name).hda

    Args:
        definition(hou.HDADefinition): The HDA definition to get the expanded name for.

    Returns:
        (str): The expanded HDA name.
    """
    category = definition.nodeTypeCategory().name()
    current_name = definition.nodeTypeName()
    name = nodetypeutils.node_type_name(current_name)
    namespace = nodetypeutils.node_type_namespace(current_name)
    version = nodetypeutils.node_type_version(current_name)
    return "{category}_{namespace}{name}.{version}.hda".format(
        category=category,
        namespace="{namespace}.".format(namespace=namespace) if namespace else "",
        name=name,
        version=version,
    )
