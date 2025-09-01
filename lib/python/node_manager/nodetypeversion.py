#!/usr/bin/env python

"""Node manager node type version."""

import logging

import hou

from node_manager.utils import definitionutils


logger = logging.getLogger(__name__)


class NodeTypeVersion(object):
    """NodeTypeVersion - Details about a specific version of a Node Type."""

    def __init__(
        self,
        path,
        definition=None,
        install=False,
        hidden=False,
    ):
        """
        Initialise the NodeTypeVersion.

        Args:
            path(str): The path to the Node definition file that containst this version.
            definition(:obj:`hou.HDADefinition`,optional): The definition for this
                version.
            install(:obj:`bool`,optional): Should this version be installed.
            hidden(:obj:`bool`,optional): Is this version hidden from the user.
        """
        logger.debug("Initialised NodeTypeVersion: {version}".format(version=self))
        self.path = path
        self.definition = definition
        self.installed = False
        if install:
            self.install_definition(hidden=hidden)

    def install_definition(self, hidden=False):
        """Install this definition into the current Houdini session.

        Args:
            hidden(:obj:`bool`,optional): Is this version hidden from the user.
        """
        path = self.definition.libraryFilePath()
        hou.hda.installFile(
            path,
            oplibraries_file="Scanned Asset Library Directories",
            force_use_assets=True,
        )

        # Hide the node type if required.
        self.definition.nodeType().setHidden(hidden)

        self.installed = True
        logger.info(f"Installed file {path}{' <hidden>' if hidden else ''}")

        definitionutils.cleanup_embedded_definitions(self.definition.nodeType())
