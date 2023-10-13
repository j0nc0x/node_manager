#!/usr/bin/env python

"""Node manager menu utilities."""

import logging
import sys

import hdefereval

from node_manager import manager

logger = logging.getLogger(__name__)


def get_node_manager():
    """Find the NodeManager instance stored in the current session.

    Returns:
        (HDAManager): The instance for the running Node manager.
    """
    return manager.NodeManager.init()


def edit(current_node):
    """Edit edit of the selected node.

    Args:
        current_node(hou.Node): The node to edit.
    """
    logger.debug("Edit.")
    man = get_node_manager()
    man.edit_definition(current_node)


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
