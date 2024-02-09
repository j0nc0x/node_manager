#!/usr/bin/env python

"""Run HDA publish."""

import pyblish.api

from node_manager import utils


class RunPublish(pyblish.api.InstancePlugin):
    """Pyblish plugin to continue with the HDA publish."""

    order = pyblish.api.ExtractorOrder
    label = "Houdini HDA - Run Publish"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(pyblish.plugin.Instance): The pyblish instance being processed.
        """
        node = instance.data["publish_node"]
        assert node, "No publish node found."

        man = utils.get_manager()
        man.publish_definition(node)

        # Clean up the UI.
        man.context["pyblish_ui"].destroy()
        man.context["pyblish_ui"] = None
        man.context["pyblish_node"] = None
