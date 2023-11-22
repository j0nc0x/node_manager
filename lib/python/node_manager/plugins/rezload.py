#!/usr/bin/env python

"""Rez Load Plugin that will load a set of node definitions from a rez package directory."""


import json
import logging
import os

from node_manager import utils

logger = logging.getLogger(__name__)


class NodeManagerPlugin(object):
    """Rez Load Plugin."""

    name = "RezLoad"
    plugin_type = "load"

    def __init__(self):
        """Initialise the DefaultLoad plugin."""
        self.manager = utils.get_manager()
        self.repo = self.manager.get_release_repo()
        self.extensions = [
            ".hda",
            ".hdanc",
            ".otl",
            ".otlnc",
        ]
        if self.repo  and self.repo.context:
            self.repo.context["repo_load_path"] = os.path.join(self.repo.context.get("repo_path"), "dcc", "houdini", "hda")

        self.repo_conf_data = self.load_config()

        self.repo.context["git_repo_path"] = self.repo_conf_data.get("repo_url")

        logger.debug("Initialise DefaultLoad.")

    def _config_path(self):
        """Get the path to the config file.
        
        Returns:
            (str): The path to the config file.
        """
        return os.path.join(self.repo.context.get("repo_path"), "config", "config.json")

    def load_config(self):
        """Load the repo config file.

        Returns:
            (dict): The repo config data.
        """
        config_path = self._config_path()
        logger.debug("Loading config from: {config_path}".format(config_path=config_path))

        repo_conf_data = {}
        if os.path.isfile(config_path):
            with open(config_path, "r") as repo_conf:
                repo_conf_data = json.load(repo_conf)
        else:
            logger.warning("No config found at {path}, skipping.".format(path=config_path))
        logger.debug("Config data: {data}".format(data=repo_conf_data))
        return repo_conf_data

    def get_node_definition_files(self):
        """Get a list of node definition files in the given directory.

        Returns:
            list: A list of node definition files.
        """
        load_path = self.repo.context.get("repo_load_path")
        return [
            os.path.join(load_path, node_definition_file)
            for node_definition_file in os.listdir(load_path)
            if os.path.splitext(node_definition_file)[1] in self.extensions
        ]

    def load(self):
        """Load the Node Manager repository.

        Returns:
            list: A list of node definition files.
        """
        node_definition_files = self.get_node_definition_files()
        logger.debug("Loading node definition files: {files}".format(files=node_definition_files))
        return node_definition_files
