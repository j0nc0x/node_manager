#!/usr/bin/env python

"""Node manager node type."""

import logging

from node_manager import nodetypeversion
from node_manager.utils import nodetypeutils
from node_manager.utils import definitionutils

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

    def remove_version(self, definition):
        """
        Remove the NodeTypeVersion for the given definition.

        Args:
            definition(hou.HDADefinition): The definition to remove the version for.

        Raises:
            RuntimeError: The version couldn't be removed.
        """
        path = definition.libraryFilePath()
        current_name = definition.nodeTypeName()
        version = nodetypeutils.node_type_version(current_name)
        if not version:
            version = "no version"

        # Get a list of nodetype definitions for the given version
        version_definitions = self.get_version(version)
        index = 0
        for node_type_version in version_definitions:
            if path == node_type_version.path:
                self.remove_version_at_index(version, index)

                # Uninstall the .hda file
                definitionutils.uninstall_definition(
                    definition, backup_dir=self.manager.context.get("backup_dir")
                )
                logger.debug(
                    "Removed Version {version} from {nodetype}".format(
                        version=version, nodetype=self.name
                    )
                )
                return
            index += 1

        raise RuntimeError("Couldn't remove version for {path}".format(path=path))

    def remove_version_at_index(self, version, index):
        """
        Given a version and an index remove the associated NodeTypeVersion.

        Args:
            version(str): The version number to remove.
            index(int): The version index to remove.

        Raises:
            RuntimeError: Invalid version or index provided.
        """
        if not self.get_version(version):
            raise RuntimeError("Version not found: {version}".format(version=version))

        if not index < len(self.get_version(version)):
            raise RuntimeError("Invalid index: {index}".format(index=index))

        # Remove the NodeTypeVersion
        del self.get_version(version)[index]

    def get_version(self, version):
        """
        Get any NodeTypeVersions for the given version.

        Args:
            version(str): The version to get the NodeTypeVersions for.

        Returns:
            (list): A list of NodeTypeVersions for the given version.
        """
        if version in self.versions:
            return self.versions.get(version)

        logger.debug(
            "Version {version} for {name} doesn't exist.".format(
                version=version, name=self.name
            )
        )
        return list()

    def all_versions(self):
        """
        Get all the versions of the node type.

        Returns:
            (dict): A dictionary of all of the versions of the node type.
        """
        return self.versions
