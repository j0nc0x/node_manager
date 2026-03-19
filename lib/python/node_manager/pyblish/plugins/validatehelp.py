#!/usr/bin/env python

"""Validate node parameter help."""

import pyblish.api


class ValidateHelp(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate that all parameters have help text."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Parameter Help"
    families = ["node_manager"]

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(pyblish.plugin.Instance): The pyblish instance being processed.

        Raises:
            RuntimeError: Parameters found without help text.
        """
        node = instance.data["publish_node"]
        assert node, "No publish node found."

        definition = node.type().definition()
        assert definition, "No definition found for node."

        parm_templates_group = definition.parmTemplateGroup()
        missing_help = []
        if parm_templates_group:
            for parm_template in parm_templates_group.parmTemplates():
                # We only care about parameters that are not folders or separators
                if parm_template.type() in [
                    # Add any types that shouldn't require help here
                ]:
                    continue

                if not parm_template.help():
                    missing_help.append(parm_template.name())

        if missing_help:
            self.log.warning(
                "The following parameters are missing help text: {parms}".format(
                    parms=", ".join(missing_help)
                )
            )
            # We use warning for now to "encourage" but not "require"
            # If we wanted to require it, we would raise a RuntimeError
            # raise RuntimeError("Missing help text for parameters: {parms}".format(parms=", ".join(missing_help)))
