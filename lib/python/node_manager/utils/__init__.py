#!/usr/bin/env python

from node_manager import manager


def get_manager():
    """Get the node manager instance if one exists.

    Returns:
        node_manager.NodeManager: The current instance of Node Manager.
    """
    manager_instance = manager.NodeManager.instance
    if not manager_instance:
        raise RuntimeError("Node Manager not initialised.")
    return manager_instance
