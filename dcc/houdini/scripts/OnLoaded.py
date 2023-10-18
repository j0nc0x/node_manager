#!/usr/bin/env python

"""Houdini Callback for when a node is loaded."""

import logging

from node_manager.utils import callbacks


logger = logging.getLogger(__name__)


current_node = kwargs.get("node", None)
logger.debug("OnCreated: {node}".format(node=current_node.name()))

callbacks.node_created_or_loaded(current_node)