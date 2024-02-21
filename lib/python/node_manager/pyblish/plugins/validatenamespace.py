#!/usr/bin/env python

"""Validate node namespace."""

import pyblish.api

from node_manager import config
from node_manager import utils
from node_manager.utils import nodetypeutils


class ValidateNamespace(pyblish.api.InstancePlugin):
    """Pyblish plugin to validate the namespace of the collected node."""

    order = pyblish.api.ValidatorOrder
    label = "Houdini HDA - Namespace"
    families = ["node_manager"]

    def process(self, instance):
        """Pyblish process method.

        Args:
            instance(pyblish.plugin.Instance): The pyblish instance being processed.

        Raises:
            RuntimeError: Invalid namespace found.
        """
        node = instance.data["publish_node"]
        assert node, "No publish node found."

        node_type_name = node.type().name()
        namespace = nodetypeutils.node_type_namespace(node_type_name)
        self.log.info(
            "Checking namespace for {node}: {namespace}".format(
                node=node_type_name,
                namespace=namespace,
            )
        )

        allowed_namespaces = config.node_manager_config.get("namespaces", [])
        assert allowed_namespaces, "No namespaces defined in config."
        allowed_namespaces = utils.expand_namespaces(allowed_namespaces)
        self.log.info("Allowed namespaces {allowed_namespaces}".format(allowed_namespaces=allowed_namespaces))

        if namespace not in allowed_namespaces:
            raise RuntimeError(
                "Invalid namespace for {node}: {namespace}".format(
                    node=node_type_name,
                    namespace=namespace,
                )
            )
