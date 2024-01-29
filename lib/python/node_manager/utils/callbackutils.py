#!/usr/bin/env python

"""Handle callbacks relating to the NodeManager."""

import logging

import hou

from node_manager import config
from node_manager import utils
from node_manager.utils import nodeutils


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


def node_changed(current_node):
    """Handle a node being created or loaded.

    Args:
        current_node(hou.Node): The node that was created or loaded.
    """
    manager = utils.get_manager()
    if not manager:
        logger.debug("Node manager not available, skipping.")
        return
    elif not cosmetic_callbacks_enabled():
        logger.debug("UI unavailable, cosmetic callbacks disabled.")
        return
    else:
        logger.debug("UI available, cosmetic callbacks enabled.")

    # Is the node a digital asset?
    if not nodeutils.is_digital_asset(
        current_node.path(),
        include_hidden=config.node_manager_config.get("include_all_hdas", False)
    ):
        logger.debug(
            "Skipping node that isn't a NodeManager digital asset: {node}".format(
                node=current_node.name(),
            )
        )
        return

    # We created or loaded a NodeManager node
    logger.debug("NodeCreatedOrLoaded: {node}".format(node=current_node.name()))
    nodeutils.node_comment(
        current_node, published=manager.is_node_manager_node(current_node)
    )
