#!/usr/bin/env python

"""Node manager menu utilities."""

import logging

from node_manager import manager

logger = logging.getLogger(__name__)


def get_node_manager():
    """Find the NodeManager instance stored in the current session.

    Returns:
        (HDAManager): The instance for the running Node manager.
    """
    return manager.NodeManager.init()


def publish(current_node):
    """Publish Definition callback.

    Args:
        current_node(hou.Node): The node to publish the definition for.
    """
    man = get_node_manager()
    man.prepare_publish(current_node)
