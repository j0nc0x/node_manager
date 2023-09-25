#!/usr/bin/env python

"""Node manager menu utilities."""

import logging

import hdefereval

from node_manager import manager

logger = logging.getLogger(__name__)


def get_node_manager():
    """Find the NodeManager instance stored in the current session.

    Returns:
        (HDAManager): The instance for the running Node manager.
    """
    return manager.NodeManager.init()


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
    man = get_node_manager()
    method = getattr(man, method_name, None)
    if (
        man
        and hasattr(man, method_name)
        and callable(getattr(man, method_name))
    ):
        method = getattr(man, method_name)
        hdefereval.executeDeferred(method, node)
    else:
        hdefereval.executeDeferred(menu_error, method_name)
