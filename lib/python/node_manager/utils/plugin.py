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


def import_plugins():
    """Import all plugins found from the $NODE_MANAGER_PLUGINS_PATH environment
    variable, returing a list of initialised plugins.

    Returns:
        list: A list of initialised plugins.
    """
    plugins = []
    for plugin_path in os.environ.get("NODE_MANAGER_PLUGINS_PATH", "").split(":"):
        print(plugin_path)
        if plugin_path:
            plugins.extend(import_plugins_from_path(plugin_path))

    return plugins


def import_plugins_from_path(plugin_path):
    """Import all plugins found in the given plugin_path, returing a list of
    initialised plugins.

    Args:
        plugin_path(str): The path to the plugins to import.

    Returns:
        list: A list of initialised plugins.
    """
    plugins = []
    for path in [
        os.path.join(plugin_path, plugin_file)
        for plugin_file
        in os.listdir(plugin_path)
        if not plugin_file.startswith("__")
        and not plugin_file.startswith(".")
        and plugin_file.endswith(".py")
    ]:
        plugin_module = path_import(path)
        logger.info(
            "Plugin imported from: {plugin_path}".format(
                plugin_path=path,
            )
        )
        plugins.append(plugin_module)

    return plugins


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


def get_load_plugin(load_plugin_name, repo):
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
                repo=repo,
            )


def get_edit_plugin(edit_plugin_name):
    """Get the given edit plugin.

    Args:
        edit_plugin_name(str): The name of the edit plugin to get.

    Returns:
        object: The load plugin.
    """
    manager_instance = utils.get_manager()
    if edit_plugin_name:
        edit_plugin = edit_plugin_name
    else:
        edit_plugin = "DefaultEdit"

    for plugin_module in manager_instance._plugins:
        if plugin_module.NodeManagerPlugin.name == edit_plugin:
            return initialise_plugin(
                plugin_module,
            )


def get_release_plugin(release_plugin_name):
    """Get the given release plugin.

    Args:
        release_plugin_name(str): The name of the release plugin to get.

    Returns:
        object: The release plugin.
    """
    manager_instance = utils.get_manager()
    if release_plugin_name:
        publish_plugin = release_plugin_name
    else:
        publish_plugin = "DefaultRelease"

    for plugin_module in manager_instance._plugins:
        if plugin_module.NodeManagerPlugin.name == publish_plugin:
            return initialise_plugin(
                plugin_module,
            )
