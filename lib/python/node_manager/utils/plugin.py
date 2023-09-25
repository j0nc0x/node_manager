#!/usr/bin/env python

import importlib
import logging
import os

from node_manager import utils


logger = logging.getLogger(__name__)


def path_import(plugin_path):
    """See https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly

    Args:
        plugin_path(str): The path to the plugin file to import.

    Returns:
        object: The initialised plugin.
    """
    spec = importlib.util.spec_from_file_location(plugin_path, plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def initialise_plugin(plugin_module, **kwargs):
    """Initialise the given plugin.

    Args:
        plugin_module(object): The plugin module to initialise.

    Returns:
        object: The initialised plugin.
    """
    plugin = plugin_module.NodeManagerPlugin(**kwargs)
    logger.info(
        "Plugin {plugin_name} (Type: {plugin_type})".format(
            plugin_name=plugin.name,
            plugin_type=plugin.plugin_type,
        )
    )
    return plugin


def import_plugins(plugin_path):
    """Import all plugins found in self.node_manager_plugin_path, storing the
    initialised plugins in self._plugins.

    Args:
        plugin_path(str): The path to the plugins to import.

    Returns:
        list: A list of plugins.
    """
    plugins = []
    for path in [
        os.path.join(plugin_path, plugin_file)
        for plugin_file
        in os.listdir(plugin_path)
        if not plugin_file.startswith("__") and plugin_file.endswith(".py")
    ]:
        plugin_module = path_import(path)
        logger.info(
            "Plugin imported from: {plugin_path}".format(
                plugin_path=path,
            )
        )
        plugins.append(plugin_module)

    return plugins


def get_load_plugin(load_plugin_name, repo_path, repo_root, repo_temp):
    """Get the given load plugin.

    Args:
        load_plugin_name(str): The name of the load plugin to get.

    Returns:
        object: The load plugin.
    """
    manager_instance = utils.get_manager()
    if load_plugin_name:
        load_plugin = load_plugin_name
    else:
        load_plugin = "DefaultLoad"

    for plugin_module in manager_instance._plugins:
        if plugin_module.NodeManagerPlugin.name == load_plugin:
            return initialise_plugin(
                plugin_module,
                repo_path=repo_path,
                repo_root=repo_root,
                repo_temp=repo_temp,
            )


def get_discover_plugin(discover_plugin_name):
    """Get the given discover plugin.

    Args:
        discover_plugin_name(str): The name of the discover plugin to get.

    Returns:
        object: The discover plugin.
    """
    manager_instance = utils.get_manager()
    if discover_plugin_name:
        discover_plugin = discover_plugin_name
    else:
        discover_plugin = "DefaultDiscover"

    for plugin_module in manager_instance._plugins:
        if plugin_module.NodeManagerPlugin.name == discover_plugin:
            return initialise_plugin(plugin_module)
