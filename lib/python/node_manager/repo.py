#!/usr/bin/env python

"""Handle Node Repos."""

import json
import logging
import os
import time

import hou

from node_manager import nodetype
from node_manager import utilities
from node_manager.utils import plugin


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
        self.repo_path = repo_path
        self.name = self.get_name()

        start = time.time()
        # self.git_repo = self.clone_repo()
        # self.manager.stats["repo_clone"] = time.time() - start

        # start = time.time()
        # self.build_repo()
        # self.manager.stats["build"] = time.time() - start

        self.load_plugin = self.get_load_plugin()
        self.node_manager_definition_files = self.initialise_repo()

        self.editable = editable
        self.asset_subdirectory = "hda"
        self.node_types = dict()

        self.commit_hash = None

        logger.info(
            "Initialised HDA Repo: {name} ({path})".format(
                name=self.name, path=self.repo_path
            )
        )

    def get_repo_root_dir(self):
        """Get the root directory for the HDA repo.

        Returns:
            str: The path to the HDA repo on disk."""
        return os.path.join(self.manager.base_dir, self.name)

    def get_repo_temp_dir(self):
        """Get the temp directory for the HDA repo.

        Returns:
            str: The path to the HDA repo on disk."""
        return os.path.join(self.manager.temp_dir, self.name)

    def repo_root(self):
        """"""
        return self.load_plugin.get_repo_load_path()

    def get_load_plugin(self):
        """Get the load plugin for this repo.

        Returns:
            (obj): The load plugin for this repo.
        """
        load_plugin = plugin.get_load_plugin(
            self.manager.load_plugin,
            self.repo_path,
            self.get_repo_root_dir(),
            self.get_repo_temp_dir(),
        )
        if not load_plugin:
            raise RuntimeError("Couldn't find Node Manager Load Plugin.")

        return load_plugin

    def initialise_repo(self):
        """Initialise the NodeRepo.

        Returns:
            list(NodeRepo): A list of NodeRepo objects.
        """
        return self.load_plugin.load()

    def config_path(self):
        """
        """
        return os.path.join(self.get_repo_root_dir(), "config", "config.json")

    # def repo_root(self):
    #     """Get the root of the HDA repo on the filesystem.

    #     Returns:
    #         (str): The path to the HDA repo on disk.
    #     """
    #     # if self.editable:
    #     #     return self.repo_path

    #     return os.path.dirname(self.library_path)

    def get_name(self):
        """Get the repo name.

        Returns:
            (str): The name of the Node repo.
        """
        # repo_conf_path = self.config_path()
        # repo_conf_data = None
        # with open(repo_conf_path, "r") as repo_conf:
        #     repo_conf_data = json.load(repo_conf)

        # if not repo_conf_data:
        #     logger.warning(
        #         "Repo conf failed to load from {path}".format(
        #             path=repo_conf_path,
        #         )
        #     )
        #     return

        # name = repo_conf_data.get("name")
    
        return self.repo_path.split("/")[-1][:-4]

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

    def load_nodes(self):
        """Load all definitions contained by this repository."""
        logger.debug(
            "Reading from {directory}".format(
                directory=self.get_repo_temp_dir(),
            )
        )

        for definition_file in self.node_manager_definition_files:
            self.process_node_definition_file(definition_file)

    def add_definition_copy(self, definition, namespace=None, name=None, version=None):
        """Create a copy of a node definition.

        Update the nodeTypeName if required.

        Args:
            definition(hou.HDADefinition): The node definition to copy.
            namespace(:obj:`str`,optional): The node namespace to use for the copy.
            name(:obj:`str`,optional): The node name to use for the copy.
            version(:obj:`str`,optional): The node version to use for the copy.

        Returns:
            (str): The name of the copied node.
        """
        logger.debug(
            "Adding definition {definition} to repo {repo}".format(
                definition=definition.nodeTypeName(),
                repo=self.name,
            )
        )
        logger.debug(
            "Updating namespace: {namespace}, name: {name}, version: {version}".format(
                namespace=namespace,
                name=name,
                version=version,
            )
        )
        # Write the HDA to the edit_dir
        editable_path = utilities.editable_hda_path_from_components(
            definition, self.manager.edit_dir, namespace=namespace, name=name
        )
        logger.debug("Editable path: {path}".format(path=editable_path))

        # See if we are updating the NodeTypeName
        if namespace or name or version:
            new_name = utilities.node_type_name_from_components(
                definition, namespace=namespace, name=name, version=version
            )
            logger.debug("Using new name: {new_name}".format(new_name=new_name))
        else:
            new_name = None

        definition.copyToHDAFile(editable_path, new_name=new_name)
        logger.debug("Definition saved to {path}".format(path=editable_path))

        # Add the newly written HDA to the HDA Manager
        self.process_node_definition_file(editable_path, force=True)

        return new_name
