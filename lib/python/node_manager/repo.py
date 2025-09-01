#!/usr/bin/env python

"""Handle Node Repos."""

import json
import logging
import os

import hou

from node_manager import nodetype
from node_manager import utils
from node_manager.utils import nodetypeutils
from node_manager.utils import pluginutils


logger = logging.getLogger(__name__)


class NodeRepo(object):
    """Node Repository - associated with a rez package that contains Node Definitions."""

    def __init__(
        self,
        manager,
        repo_path,
        editable=False,
    ):
        """Initialise the HDA repo.

        Args:
            manager(HDAManager): An instance of the Node manager currently being used.
            repo_path(str): The path on disk to where the HDA repository is located.
            editable(:obj:`bool`,optional): Are the HDAs in this repository editable?
        """
        self.manager = manager
        self.context = {}
        self.config = {}

        self.context["repo_path"] = repo_path
        self.context["repo_name"] = self.get_name()

        self.editable = editable
        self.asset_subdirectory = "hda"
        self.node_types = dict()

        self.commit_hash = None

        logger.info(
            "Initialised HDA Repo: {name} ({path})".format(
                name=self.context.get("repo_name"),
                path=self.context.get("repo_path"),
            )
        )

    def get_repo_backup_dir(self):
        """Get the backup directory for the HDA repo.

        Returns:
            str: The path to the HDA repo backup directory.
        """
        backup_directory = os.path.join(
            self.context.get("repo_path"), ".node_manager_backup"
        )
        if not os.path.isdir(backup_directory):
            os.mkdir(backup_directory)
            logger.debug(
                "Created backup directory: {path}".format(path=backup_directory)
            )
        return backup_directory

    def get_load_plugin(self):
        """Get the load plugin for this repo.

        Returns:
            (obj): The load plugin for this repo.
        """
        logger.debug(
            "Using load plugin: {plugin}".format(plugin=self.manager.load_plugin)
        )
        load_plugin = pluginutils.get_load_plugin(
            self.manager.load_plugin,
        )
        if not load_plugin:
            raise RuntimeError("Couldn't find Node Manager Load Plugin.")

        return load_plugin

    def initialise_repo(self):
        """Initialise the NodeRepo.

        Returns:
            list(NodeRepo): A list of NodeRepo objects.
        """
        load_plugin = self.get_load_plugin()
        self.node_manager_definition_files = load_plugin.load()
        self.load_config()

    def load_config(self):
        """Load the repo config.
        
        Raises:
            RuntimeError: Config file not found.
        """
        config_path = self.context.get("config_path")

        if not config_path:
            logger.warning("No config path set, skipping.")
            return

        if not os.path.isfile(config_path):
            raise RuntimeError(f"Config file not found: {config_path}")

        with open(config_path, "r") as repo_conf:
            self.config = json.load(repo_conf)

        logger.info(f"Repo config: {self.config}")

    def get_name(self):
        """Get the repo name.

        Returns:
            (str): The name of the Node repo.
        """
        name = self.context.get("repo_path").split("/")[-1]
        logger.debug(
            "Calculating repo name from {path} as {name}".format(
                path=self.context.get("repo_path"),
                name=name,
            )
        )

        return name

    def process_definition(self, definition):
        """Update the node_types dictionary usng the provided definition.

        Args:
            definition(hou.HDADefinition): The node definition to process.

        Returns:
            (None)
        """
        current_name = definition.nodeTypeName()
        category = definition.nodeTypeCategory().name()
        index = utils.node_type_index(current_name, category)
        name = nodetypeutils.node_type_name(current_name)
        namespace = nodetypeutils.node_type_namespace(current_name)
        version = nodetypeutils.node_type_version(current_name)

        # Add the node_type to our dictionary if it doesn't already exist
        if index not in self.node_types:
            hda_node_type = nodetype.NodeType(self.manager, name, namespace)
            self.node_types[index] = hda_node_type

        hidden = False
        for hidden_node in self.config.get("ophide", []):
            if hidden_node in current_name:
                hidden = True

        # Otherwise load as normal
        self.node_types[index].add_version(
            version,
            definition,
            hidden=hidden,
        )

    def process_node_definition_file(self, path):
        """Process the given node definition file and handle any definitions it contains.

        Args:
            path(str): The path to the node definition file we are processing.
        """
        definitions = hou.hda.definitionsInFile(path)
        for definition in definitions:
            self.process_definition(definition)

    def load_nodes(self, force=False):
        """Load all definitions contained by this repository.

        Args:
            force(:obj:`bool`,optional): Force the HDA to be installed.
        """
        if force:
            self.initialise_repo()

        for definition_file in self.node_manager_definition_files:
            logger.debug("Processing {path}".format(path=definition_file))
            self.process_node_definition_file(definition_file)

    def remove_definition(self, definition):
        """Remove the given defintion from the repo.

        Also uninistall the definition from the current session and back it up.

        Args:
            definition(hou.HDADefinition): The node definition to remove.

        Raises:
            RuntimeError: NodeType not found.
        """
        # Remove version
        current_name = definition.nodeTypeName()
        category = definition.nodeTypeCategory().name()
        index = utils.node_type_index(current_name, category)
        nodetype = self.manager.nodetype_from_definition(definition)
        nodetype.remove_version(definition)

        # Remove the nodetype if no versions remain
        if len(nodetype.versions) == 0:
            if index not in self.node_types:
                raise RuntimeError(
                    "NodeType {nodetype} not found in {repo}".format(
                        nodetype=index, repo=self.get_name()
                    )
                )
            del self.node_types[index]
            logger.debug(
                "Removed NodeType {nodetype} from {repo}".format(
                    nodetype=index, repo=self.get_name()
                )
            )
        else:
            logger.debug(
                "Nothing to remove. More than one version remains for "
                "{nodetype}.".format(nodetype=index)
            )

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
                repo=self.context.get("repo_name"),
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
        editable_path = utils.editable_hda_path_from_components(
            definition,
            self.manager.context.get("manager_edit_dir"),
            namespace=namespace,
            name=name,
        )
        logger.debug("Editable path: {path}".format(path=editable_path))

        # See if we are updating the NodeTypeName
        if namespace or name or version:
            new_name = nodetypeutils.node_type_name_from_components(
                definition, namespace=namespace, name=name, version=version
            )
            logger.debug("Using new name: {new_name}".format(new_name=new_name))
        else:
            new_name = None

        definition.copyToHDAFile(editable_path, new_name=new_name)
        logger.debug("Definition saved to {path}".format(path=editable_path))

        # Add the newly written HDA to the Node Manager
        self.process_node_definition_file(editable_path)

        return new_name
