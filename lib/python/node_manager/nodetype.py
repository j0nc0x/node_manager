#!/usr/bin/env python

"""Node manager node type."""

import logging

from node_manager import nodetypeversion

logger = logging.getLogger(__name__)


class NodeType(object):
    """NodeType - Details about Houdini NodeTypes.

    This includes a record of all available versions along with those currently loaded.
    """

    def __init__(
        self,
        manager,
        name,
        namespace,
    ):
        """
        Initialise the NodeType class.

        Args:
            manager(NodeManager): The instance of the running Node manager.
            name(str): The name of the node type.
            namespace(str): The namespace of the node type.
        """
        self.manager = manager
        self.name = name
        self.namespace = namespace
        self.versions = dict()
        logger.info(
            "Initialised NodeType: {namespace}::{name}".format(
                namespace=self.namespace, name=self.name
            )
        )

    def add_version(self, version, definition, force=False):
        """
        Add a new NodeType version to the manager.

        Args:
            version(str): The version to add the definition under.
            definition(hou.HDADefinition): The definition to add.
            force(:obj:`bool`,optional): Force the version to be added irrespective of
                the load depth.
        """
        logger.info(
            "Adding version {version} for {namespace}::{name}".format(
                version=version, namespace=self.namespace, name=self.name
            )
        )
        install = True
        path = definition.libraryFilePath()
        # if force or self.num_versions() < self.manager.depth:
        #     install = True

        node_type_version = nodetypeversion.NodeTypeVersion(
            path, definition=definition, install=install
        )

        if version is None:
            version = "no version"

        if self.versions.get(version):
            self.versions[version].append(node_type_version)
        else:
            self.versions[version] = [node_type_version]
