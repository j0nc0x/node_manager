#!/usr/bin/env python

"""Validate definition is saved."""

import pyblish.api

from node_manager.pyblish.autofix import AutoFixAction


class ValidateSaved(pyblish.api.InstancePlugin):
    """Validate if the collected node's definition is saved and ready to publish."""

    label = "Houdini HDA - Saved"
    order = pyblish.api.ValidatorOrder
    actions = [AutoFixAction]

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: Node unlocked or has unsaved changes.
        """
        for node in instance:
            if node.isEditable():
                raise RuntimeError(
                    "Node is currently unlocked. Make sure it is saved and matches "
                    "current definition before publishing."
                )
            if not node.matchesCurrentDefinition():
                raise RuntimeError("Node has unsaved changes.")

    @staticmethod
    def auto_fix(instance, action):
        """Run the auto-fix method.

        This attempts to match the node instance to its definition.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.
            action: The pyblish action taking place.
        """
        for node in instance:
            node.matchCurrentDefinition()
