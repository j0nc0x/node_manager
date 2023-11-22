#!/usr/bin/env python

"""Houdini Callback for when a node is updated (ie. its definition changes)."""

import logging

from node_manager.utils import callbackutils


logger = logging.getLogger("node_manager.dcc.houdini.scripts.OnUpdated")


current_node = kwargs.get("node", None)
logger.debug("OnUpdated: {node}".format(node=current_node.name()))

callbackutils.node_changed(current_node)
