#!/usr/bin/env python

"""Houdini node utility functions."""

import logging

import hou


logger = logging.getLogger(__name__)


def node_comment(current_node, published=True):
    """Set the comment on a node.

    Args:
        current_node(hou.Node): The node to set the comment on.
        edit(bool): Whether the node is editable or not.
    """
    if current_node.isInsideLockedHDA():
        logger.debug("Skipping locked node: {node}".format(node=current_node.name()))
        return

    state = "Published"
    if not published:
        state = "Editable"
    current_node.setComment("Node Manager: {state}".format(state=state))
    current_node.setGenericFlag(hou.nodeFlag.DisplayComment, True)
    logger.debug("Set comment on node: {node}".format(node=current_node.name()))


def node_at_path(node_path):
    """
    Get the node at a given Houdini node path.

    Args:
        node_path(str): The path to a node to return the node for.

    Returns:
        houdini_node(hou.Node): The houdini node that was found at the given scene path.
    """
    houdini_node = hou.node(node_path)
    if not houdini_node:
        logger.warning("No node found at path: {path}".format(path=node_path))

    return houdini_node


def type_name(node_path, short=True):
    """Get the name for the given node path.

    By default this returns the short name ie. 'rebellion.pipeline::dispatcher::1.0.0'
    would return 'dispatcher'.

    Args:
        node_path(str): The path to a node to query the name for.
        short(:obj:`bool`, optional): Should the short path rather than the full
            namespaced path be returned.

    Returns:
        node_name(str): The name of the node if it exists.
    """
    houdini_node = node_at_path(node_path)
    if houdini_node:
        if short:
            components = houdini_node.type().nameComponents()
            node_name = components[2]
        else:
            node_name = houdini_node.type().name()

        return node_name

    return None


def has_node_type(node_path, node_type, category=None):
    """
    Lookup if the node at the given path and category has the supplied node_type.

    Args:
        node_path(str): The path to the node to query.
        node_type(str): The node type to query against.
        category(:obj:`str`, optional): The node type category to query against.

    Returns:
        (bool): Was the match successful?
    """
    category_name = None
    if category:
        houdini_node = node_at_path(node_path)
        if houdini_node:
            category_name = houdini_node.type().category().name()

    name = type_name(node_path)
    if category and category != category_name:
        return False

    if name == node_type:
        return True

    return False


def all_nodes_of_type(node_type, node_filter=hou.nodeTypeFilter.NoFilter):
    """
    Return all the nodes of a certain node type and node filter.

    Args:
        node_type(str): The node type to query against.
        node_filter(hou.nodeTypeFilter): A node type filter that defines the category if
            Node Type to search within.

    Returns:
        node_matches(:obj:`list` of :obj:`hou.Node`): A list of Houdini nodes that match
            the query.
    """
    all_nodes = hou.root().recursiveGlob("*", filter=node_filter)
    if not all_nodes:
        return []

    node_matches = [
        houdini_node
        for houdini_node in all_nodes
        if type_name(houdini_node.path()) == node_type
    ]
    return node_matches


def get_user_data(node_path, name):
    """Query the user data based on the given node path and name.

    This is to work around an issue with how user data is handled in locked HDAs. In
    that case, any user data set using the standard hou.Node.setUserData function will
    be lost on scene save, unless it is written into the HDA (which we generally want to
    avoid). This function tries to access the userdata on the first unlocked parent node
    if the current node is locked.

    Args:
        node_path(str): The path to the node to query.
        name(str): The user data name to query.

    Returns:
        (str): The user data value for the given query.

    Raises:
        RuntimeError: Couldn't find an unlocked parent node.
    """
    houdini_node = node_at_path(node_path)
    if houdini_node:
        if not houdini_node.isInsideLockedHDA():
            logger.debug(
                "Reading User Data for '{name}' from {path}".format(
                    name=name, path=houdini_node.path()
                )
            )
            return houdini_node.userData(name)

        parent_node = houdini_node.parent()
        user_data_name = "{path}.{name}".format(path=houdini_node.path(), name=name)

        while parent_node:
            if not parent_node.isInsideLockedHDA():
                logger.debug(
                    "Reading User Data for '{name}' from {path}".format(
                        name=name, path=parent_node.path()
                    )
                )
                return parent_node.userData(user_data_name)

            parent_node = parent_node.parent()

        raise RuntimeError(
            "No unlocked parent node found for {path}".format(path=node_path)
        )

    return None


def set_user_data(node_path, name, value):
    """Set user data based on the given node path, name and value.

    This is to work around an issue with how user data is handled in locked HDAs. In
    that case, any user data set using the standard hou.Node.setUserData function will
    be lost on scene save, unless it is written into the HDA (which we generally want to
    avoid). This function tries to store the userdata on the first unlocked parent node
    if the current node is locked.

    Args:
        node_path(str): The path to the node to query.
        name(str): The user data name to query.
        value(str): The value to set into the user data.

    Returns:
        (str): The user data value for the given query.

    Raises:
        RuntimeError: Couldn't find an unlocked parent node.
    """
    houdini_node = node_at_path(node_path)
    if houdini_node:
        if not houdini_node.isInsideLockedHDA():
            logger.debug(
                "Writing User Data '{value}' for '{name}' from {path}".format(
                    value=value, name=name, path=houdini_node.path()
                )
            )
            houdini_node.setUserData(name, value)
            return

        parent_node = houdini_node.parent()
        user_data_name = "{path}.{name}".format(path=houdini_node.path(), name=name)

        while parent_node:
            if not parent_node.isInsideLockedHDA():
                logger.debug(
                    "Writing User Data '{value}' for '{name}' from {path}".format(
                        value=value, name=name, path=parent_node.path()
                    )
                )
                parent_node.setUserData(user_data_name, value)
                return

            parent_node = parent_node.parent()

        raise RuntimeError(
            "No unlocked parent node found for {path}".format(path=node_path)
        )


def definition_from_node(node_path):
    """
    For the given hou.Node return it's hou.HDADefinition.

    Args:
        node_path(str): The Houdini node path to get the definition for.

    Returns:
        (hou.HDADefinition): The definition for the given node path.
    """
    node = node_at_path(node_path)
    if node:
        node_type = node.type()
        if node_type:
            return node_type.definition()

    return None


def is_digital_asset(node_path):
    """
    Check if the given node path is a digital asset.

    Args:
        node_path(str): The Houdini node path to check.

    Returns:
        (bool): Is the node at the given path a digital asset.
    """
    if definition_from_node(node_path):
        return True

    return False


def force_ui_update(parm_paths):
    """Force a manual UI update for the given parameters.

    There is a long term bug in the Houdini UI where parms that contain a python
    expression won't update in the UI when they contain a python expression. If the
    value is queried the correct value is returned, but the UI shows the wrong value.
    Clicking on the UI item forces it to refresh.

    Args:
        parm_paths(list): A list of Houdini parameter paths to refresh in the UI.
    """
    for path in parm_paths:
        parm = hou.parm(path)
        if not parm:
            logger.warning("Parameter not found: {path}".format(path=path))

        # Force the UI to update by clicking the parm.
        parm.pressButton()
