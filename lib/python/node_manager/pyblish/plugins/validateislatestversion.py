#!/usr/bin/env python

"""Validate version."""

import pyblish.api

from node_manager import utils


class ValidateIsLatestVersion(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate if the collected node is the latest version."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Is latest version"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: Node unlocked or has unsaved changes.
        """
        for node in instance:
            m = utils.get_manager()
            if not m.is_latest_version(node):
                raise RuntimeError(
                    "{node} is not the latest version. Make sure to match the latest "
                    "version or have a higher version then the lastest version before "
                    "publishing.".format(node=node.type().name())
                )
