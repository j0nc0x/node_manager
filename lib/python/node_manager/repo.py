#!/usr/bin/env python

"""Handle Node Repos."""

import json
import logging
import os

import hou

from node_manager import nodetype
from node_manager import utilities


logger = logging.getLogger(__name__)


class NodeRepo(object):
    """Node Repository - associated with a rez package that contains Node Definitions."""

    # __config = utilities.get_config()
    # packages_root = __config.get("packages_root")

    def __init__(
        self,
        manager,
        repo_path,
        editable=False,
    ):
        """Initialise the HDA repo.

        Args:
            manager(HDAManager): An instance of the HDA manager currently being used.
            repo_path(str): The path on disk to where the HDA repository is located.
            editable(:obj:`bool`,optional): Are the HDAs in this repository editable?
        """
        self.manager = manager
        self.editable = editable
        self.repo_path = repo_path
        self.asset_subdirectory = "hda"
        self.node_types = dict()
        self.extensions = [".hda", ".hdanc"]
        self.package_name = self.get_name()
        self.package_version = None
        self.commit_hash = None

        logger.info(
            "Initialised HDA Repo: {name} ({path})".format(
                name=self.package_name, path=self.repo_path
            )
        )

    def get_name(self):
        """Get the repo name.

        Returns:
            (str): The name of the Node repo.
        """
        repo_conf_path = os.path.join(self.repo_path, ".conf")
        repo_conf_data = None
        with open(repo_conf_path, "r") as repo_conf:
            repo_conf_data = json.load(repo_conf)

        if not repo_conf_data:
            logger.warning(
                "Repo conf failed to load from {path}".format(
                    path=repo_conf_path,
                )
            )
            return

        name = repo_conf_data.get("name")

        return name

    def process_definition(self, definition, force=False):
        """Update the node_types dictionary usng the provided definition.

        Args:
            definition(hou.HDADefinition): The node definition to process.
            force(:obj:`bool`,optional): Force the version to be processed irrespective
                of if it already exists.

        Returns:
            (None)
        """
        current_name = definition.nodeTypeName()
        category = definition.nodeTypeCategory().name()
        index = utilities.node_type_index(current_name, category)
        name = utilities.node_type_name(current_name)
        namespace = utilities.node_type_namespace(current_name)
        version = utilities.node_type_version(current_name)

        # Add the node_type to our dictionary if it doesn't already exist
        if index not in self.node_types:
            hda_node_type = nodetype.NodeType(self.manager, name, namespace)
            self.node_types[index] = hda_node_type

        # Otherwise load as normal
        self.node_types[index].add_version(
            version,
            definition,
            force=force,
        )

    def process_node_definition_file(self, path, force=False):
        """Process the given node definition file and handle any definitions it contains.

        Args:
            path(str): The path to the node definition file we are processing.
            force(:obj:`bool`,optional): Force the HDA to be installed.
        """
        definitions = hou.hda.definitionsInFile(path)
        for definition in definitions:
            self.process_definition(
                definition, force=force
            )

    def load(self):
        """Load all definitions contained by this repository."""
        logger.debug("Reading from {directory}".format(directory=self.repo_path))

        if not os.path.exists(self.repo_path):
            raise RuntimeError(
                "Couldn't load from: {directory}".format(directory=self.repo_path)
            )

        for definition_file in os.listdir(self.repo_path):
            if os.path.splitext(definition_file)[1].lower() in self.extensions:
                full_path = os.path.join(self.repo_path, definition_file)
                self.process_node_definition_file(full_path)
