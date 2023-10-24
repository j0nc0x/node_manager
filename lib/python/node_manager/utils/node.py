#!/usr/bin/env python

"""NodeManager Node related utils."""

import logging

import hou


logger = logging.getLogger(__name__)


def node_comment(current_node, edit=False):
    """Set the comment on a node.

    Args:
        current_node(hou.Node): The node to set the comment on.
        edit(bool): Whether the node is editable or not.
    """
    state = "Published"
    if edit:
        state = "Editable"
    current_node.setComment("Node Manager: {state}".format(state=state))
    current_node.setGenericFlag(hou.nodeFlag.DisplayComment, True)
    logger.debug("Set comment on node: {node}".format(node=current_node.name()))
