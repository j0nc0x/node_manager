#!/usr/bin/env python

"""Node manager menu utilities."""

import logging
import sys

import hdefereval

from node_manager import manager
from node_manager.dependencies import nodes

logger = logging.getLogger(__name__)


def get_node_manager():
    """Find the NodeManager instance stored in the current session.

    Returns:
        (HDAManager): The instance for the running Node manager.
    """
    return manager.NodeManager.init()


def display_node_manager(current_node):
    # We can reject nodes straight away if they are not digital assets.
    if nodes.is_digital_asset(current_node.path()):
        return True
    else:
        return False


def edit(current_node):
    """Edit edit of the selected node.

    Args:
        current_node(hou.Node): The node to edit.
    """
    logger.debug("Edit.")
    man = get_node_manager()
    man.edit_definition(current_node)


def display_edit(current_node):
    """Should the edit menu be displayed for the given node.
    
    Args:
        current_node(hou.Node): The node to check.

    Returns:

    """
    man = get_node_manager()

    # We only want to show the edit menu for nodes managed by the node manager
    return man.is_node_manager_node(current_node)


def edit_major(current_node):
    """Major version edit of the selected node.

    Args:
        current_node(hou.Node): The node to edit.
    """
    logger.debug("Edit Major.")
    man = get_node_manager()
    man.edit_definition(current_node, major=True)


def edit_minor(current_node):
    """Minor version edit of the selected node.

    Args:
        current_node(hou.Node): The node to edit."""
    logger.debug("Edit minor.")
    man = get_node_manager()
    man.edit_definition(current_node, minor=True)


def discard(current_node):
    """Discard edit of the selected node.

    Args:
        current_node(hou.Node): The node to edit.
    """
    logger.debug("Discard.")
    man = get_node_manager()
    man.discard_definition(current_node)


def display_discard(current_node):
    """Should the discard menu be displayed for the given node.

    Args:
        current_node(hou.Node): The node to check.

    Returns:

    """
    man = get_node_manager()

    # We only want to show the discard menu for nodes not managed by the node manager
    return not man.is_node_manager_node(current_node)


def display_publish(current_node):
    """Should the publish menu be displayed for the given node.

    Args:
        current_node(hou.Node): The node to check.

    Returns:
        (bool): Should the publish menu be displayed?
    """
    man = get_node_manager()

    # We only want to show the publish menu for nodes not managed by the node manager
    return not man.is_node_manager_node(current_node)


def prepare_publish(current_node):
    """Prepare a node for publishing.

    Args:
        current_node(hou.Node): The node to prepare for publishing.
    """
    man = get_node_manager()
    man.prepare_publish(current_node)


def menu_error(method_name):
    """Raise a menu error.

    Args:
        method_name(str): The method_name to raise an error for.
    """
    message = "Node Manager menu callback method not found: {name}".format(
        name=method_name,
    )
    logger.error(message)
    raise RuntimeError(message)


def run_menu_callback(method_name, node, **kwargs):
    """Run node manager menu callback.

    Args:
        method_name(str): The method name to call.
        node(hou.Node): The houdini node the menu callback was called from.
    """
    current_module = sys.modules[__name__]
    if (
        hasattr(current_module, method_name)
        and callable(getattr(current_module, method_name))
    ):
        method = getattr(current_module, method_name)
        hdefereval.executeDeferred(method, node)
    else:
        hdefereval.executeDeferred(menu_error, method_name)
