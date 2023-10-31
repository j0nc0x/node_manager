#!/usr/bin/env python

"""Houdini Callback for when a node is updated (ie. its definition changes)."""

import logging

from node_manager.utils import callbacks


logger = logging.getLogger(__name__)


current_node = kwargs.get("node", None)
logger.debug("OnUpdated: {node}".format(node=current_node.name()))

callbacks.node_changed(current_node)
