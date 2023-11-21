#!/usr/bin/env python

"""Houdini Callback for when a node is loaded."""

import logging

from node_manager.utils import callbacks


logger = logging.getLogger("node_manager.dcc.houdini.scripts.OnLoaded")


current_node = kwargs.get("node", None)
logger.debug("OnCreated: {node}".format(node=current_node.name()))

callbacks.node_changed(current_node)
