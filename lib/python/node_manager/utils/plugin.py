import importlib
import logging
import os


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


def initialise_plugin(plugin_module, manager=None):
    """
    """
    if manager:
        plugin = plugin_module.NodeManagerPlugin(manager)
    else:
        plugin = plugin_module.NodeManagerPlugin()
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


def get_load_plugin(load_plugin_name, plugins, manager):
    """
    """
    if load_plugin_name:
        load_plugin = load_plugin_name
    else:
        load_plugin = "DefaultLoad"

    for plugin_module in plugins:
        if plugin_module.NodeManagerPlugin.name == load_plugin:
            return initialise_plugin(plugin_module, manager)


def get_discover_plugin(discover_plugin_name, plugins, manager):
    """
    """
    if discover_plugin_name:
        discover_plugin = discover_plugin_name
    else:
        discover_plugin = "DefaultDiscover"

    for plugin_module in plugins:
        if plugin_module.NodeManagerPlugin.name == discover_plugin:
            return initialise_plugin(plugin_module, manager)
