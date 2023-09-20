#!/usr/bin/env python

"""Handle Node Repos."""

import json
import logging
import os
import subprocess
import time

import hou

from git import Repo
from git.exc import NoSuchPathError, InvalidGitRepositoryError

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

        print(plugin.get_load_plugin(self.manager.load_plugin))

        start = time.time()
        self.git_repo = self.clone_repo()
        self.manager.stats["repo_clone"] = time.time() - start
        self.library_path = self.get_library_path()

        start = time.time()
        self.build_repo()
        self.manager.stats["build"] = time.time() - start

        self.editable = editable
        self.asset_subdirectory = "hda"
        self.node_types = dict()
        self.extensions = [".hda", ".hdanc"]

        self.version = self.get_version()
        self.commit_hash = None

        logger.info(
            "Initialised HDA Repo: {name} ({path})".format(
                name=self.name, path=self.repo_path
            )
        )

    def local_repo_root(self):
        return os.path.join(self.manager.base, self.name)

    def repo_temp_dir(self):
        return os.path.join(self.manager.temp_dir, self.name)

    def config_path(self):
        """
        """
        return os.path.join(self.local_repo_root(), "config", "config.json")

    def clone_repo(self):
        cloned_repo = None
        try:
            cloned_repo =  Repo(self.local_repo_root())
            cloned_repo.git.pull()
        except (NoSuchPathError, InvalidGitRepositoryError) as error:
            logger.debug("Couldn't load repo from {path}, clone instead.".format(path=self.local_repo_root()))

        if not cloned_repo:
            cloned_repo = Repo.clone_from(self.repo_path, self.local_repo_root(), depth=1)

        return cloned_repo

    def build_repo(self):
        os.makedirs(self.repo_temp_dir())
        expanded_hda_dir = os.path.join(self.local_repo_root(), "dcc", "houdini", "hda")
        for hda in os.listdir(expanded_hda_dir):
            path = os.path.join(expanded_hda_dir, hda)
            hda_path = os.path.join(self.repo_temp_dir(), hda)
            logger.info("Processing {source}".format(source=path))
            hotl_cmd = ["hotl", "-C", path, hda_path]
            logger.debug(hotl_cmd)
            result = subprocess.call(hotl_cmd)

    def get_library_path(self):
        config_path = self.config_path()
        repo_conf_data = {}
        with open(config_path, "r") as repo_conf:
            repo_conf_data = json.load(repo_conf)

        return repo_conf_data.get("library_path")

    def repo_root(self):
        """Get the root of the HDA repo on the filesystem.

        Returns:
            (str): The path to the HDA repo on disk.
        """
        # if self.editable:
        #     return self.repo_path

        return os.path.dirname(self.library_path)

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

    def get_version(self):
        """Get the repo version.

        Returns:
            (str): The version of the Node repo.
        """
        repo_conf_path = self.config_path()
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

        version = repo_conf_data.get("version")

        return version

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
        logger.debug("Reading from {directory}".format(directory=self.repo_temp_dir()))

        if not os.path.exists(self.library_path):
            raise RuntimeError(
                "Couldn't load from: {directory}".format(directory=self.repo_temp_dir())
            )

        for definition_file in os.listdir(self.repo_temp_dir()):
            if os.path.splitext(definition_file)[1].lower() in self.extensions:
                full_path = os.path.join(self.repo_temp_dir(), definition_file)
                self.process_node_definition_file(full_path)
