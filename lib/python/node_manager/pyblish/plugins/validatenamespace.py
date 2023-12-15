#!/usr/bin/env python

"""Validate node namespace."""

import pyblish.api

from node_manager import utils
from node_manager.utils import nodetypeutils


class ValidateNamespace(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate the namespace of the collected node."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Namespace"

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(:obj:`list` of :obj:`hou.Node`): The Houdini node instances we are
                validating.

        Raises:
            RuntimeError: Invalid namespace found.
        """
        for node in instance:
            node_type_name = node.type().name()
            namespace = nodetypeutils.node_type_namespace(node_type_name)
            self.log.info("Checking namespace for {node} is {namespace}".format(node=node_type_name, namespace=namespace))

            valid_namespace = True
            try: 
                valid_namespace =  utils.validate_namespace(namespace)
            except RuntimeError:
                self.log.warning("No namespaces defined for the current session. Skipping validation.")

            if not valid_namespace:
                raise RuntimeError(
                    "Invalid namespace for {node}".format(
                        node=node_type_name,
                    )
                )
