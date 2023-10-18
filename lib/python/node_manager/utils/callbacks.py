#!/usr/bin/env python

"""Handle callbacks relating to the NodeManager."""

import logging

import hou

from node_manager import utils
from node_manager.utils import node
from node_manager.dependencies import nodes


logger = logging.getLogger(__name__)


def cosmetic_callbacks_enabled():
    if not hou.isUIAvailable():
        return False

    try:
        _ = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        enabled = True
    except hou.NotAvailable:
        logger.info("Caught error, network editor not available.")
        enabled = False
        
    return enabled

def node_created_or_loaded(current_node):
    """Handle a node being created or loaded.

    Args:
        current_node(hou.Node): The node that was created or loaded.
    """
    if not cosmetic_callbacks_enabled():
        logger.info("UI unavailable, cosmetic callbacks disabled.")
        return
    else:
        logger.debug("UI available, cosmetic callbacks enabled.")

    # Is the node a digital asset?
    logger.debug(current_node)
    logger.debug(current_node.path())
    if not nodes.is_digital_asset(current_node.path()):
        logger.debug(
            "Skipping node that isn't digital asset: {node}".format(
                node=current_node.name(),
            )
        )
        return

    # Is the node a NodeManager node?
    manager = utils.get_manager()
    edit = True
    if not manager.is_node_manager_node(current_node):
        edit = False

    # We created or loaded a NodeManager node
    logger.debug("NodeCreatedOrLoaded: {node}".format(node=current_node.name()))
    node.node_comment(current_node, edit=edit)
    node.node_graphic(current_node, edit=edit)
