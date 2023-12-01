#!/usr/bin/env python

"""Validate publish is allowed."""

import pyblish.api

from rbl_pipe_hdamanager import utilities


class ValidatePublishAllowed(pyblish.api.InstancePlugin):
    """Validate if publishing is currently allowed to the target repo."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Publish Allowed"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: HDA publish is disabled.
        """
        allow_publish = utilities.allow_publish()
        for node in instance:
            if not allow_publish:
                raise RuntimeError("Publishing currently disabled.")
