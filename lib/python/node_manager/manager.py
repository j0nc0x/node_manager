#!/usr/bin/env python

"""HDA manager."""

import getpass
import logging
import os
import subprocess
import time

from tempfile import mkdtemp

import hou

from packaging.version import parse

if hou.isUIAvailable():
    from hdefereval import do_work_in_background_thread
else:
    do_work_in_background_thread = None

from node_manager import release
from node_manager import utilities
from node_manager.utils import plugin
from node_manager.dependencies import dialog
from node_manager.dependencies import nodes

logger = logging.getLogger(__name__)


class NodeManager(object):
    """Main HDA Manager Class."""

    instance = None
    plugin_path = "/Users/jcox/source/github/node_manager/lib/python/node_manager/plugins" # Read from env var
    discover_plugin = None
    load_plugin = "GitLoad"
    release_plugin = "GitRelease"
    # publish_node = None
    # validator_ui = None

    @classmethod
    def init(cls):
        """
        Initialise the HDAManager storing the instance in the class.

        Returns:
            (HDAManager): The HDAManager instance.
        """
        if cls.instance is None:
            start = time.time()
            cls.instance = cls()
            cls.instance.stats["init"] = time.time() - start
        return cls.instance

    def __init__(
        self,
    ):
        """Initialise the NodeManager class."""
        logger.info("Initialising Node Manager")
        self.stats = {}

    def load(self):
        """Load the HDA Manager."""
        self._plugins = plugin.import_plugins(self.plugin_path)

        self.context = {}
        self.context["temp_dir"] = mkdtemp(prefix="node-manager-")
        self.context["base_dir"] = self.get_base_dir()
        self.context["edit_dir"] = self.get_edit_dir()
        self.context["backup_dir"] = os.path.join(self.context.get("edit_dir"), "backup")
        # self.setup_callbacks()
        self.releases = list()
        self.node_repos = self.initialise_repos()
        start = time.time()
        self.load_all()
        self.stats["load_hdas"] = time.time() - start

    def initialise_repos(self):
        """Initialise the NodeRepos.

        Returns:
            list(NodeRepo): A list of NodeRepo objects.
        """
        discover_plugin = plugin.get_discover_plugin(self.discover_plugin, )
        if not discover_plugin:
            raise RuntimeError("Couldn't find Node Manager Discover Plugin.")

        return discover_plugin.discover()

    # def save(self, current_node):
    #     definition = current_node.type().definition()
    #     save_path = definition.libraryFilePath()
    #     install = False
    #     if save_path.startswith(self.temp_dir):
    #         logger.info("Saving HDA to node manager edit directory.")
    #         hda_filename = os.path.basename(save_path)
    #         save_path = os.path.join(self.edit_dir, hda_filename)
    #         install = True

    #     definition.updateFromNode(current_node)
    #     definition.save(save_path)

    #     if install:
    #         hou.hda.installFile(
    #             save_path,
    #             oplibraries_file="Scanned Asset Library Directories",
    #             force_use_assets=True,
    #         )

    # def save_hda_callback(self, asset_definition, **kwargs):
    #     print("before save HDA")
    #     print(asset_definition)
    #     print(kwargs)

    # def setup_callbacks(self):
    #     """
    #     """
    #     hou.hda.addEventCallback((hou.hdaEventType.BeforeAssetSaved, ), self.save_hda_callback)

    # def is_initialised(self):
    #     """
    #     """
    #     return self.initialised

    def get_base_dir(self):
        """Get the base directory for the HDA Manager from the
        NODE_MANAGER_BASE env var.

        Returns:
            str: The base directory for the HDA Manager.
        """
        base_dir = os.getenv("NODE_MANAGER_BASE")
        if not base_dir:
            base_dir = self.context.get("temp_dir")
            os.environ["NODE_MANAGER_BASE"] = self.context.get("temp_dir")
        return base_dir

    def get_edit_dir(self, create_on_disk=True):
        """Get the edit directory for the HDA Manager.

        Args:
            create_on_disk(bool): Should the directory be created on disk if
                it doesn't exist?

        Returns:
            str: The edit directory for the HDA Manager.
        """
        edit_dir = os.path.join(self.context.get("base_dir"), "edit", getpass.getuser())
        if create_on_disk:
            os.makedirs(edit_dir, exist_ok=True)
        return edit_dir

    def git_dir(self):
        """
        """
        return os.path.join(self.context.get("temp_dir"), "git")

    def load_all(self):
        """Load all node definitions from the repositories."""
        for repo_name in self.node_repos:
            self.node_repos.get(repo_name).load_nodes()

    def nodetype_from_definition(self, definition):
        """
        Retrieve the nodetype for the given definition.

        Args:
            definition(hou.HDADefinition): The HDA definition to use when
                looking up the HDA Manager nodetype.

        Returns:
            node_type(rbl_pipe_hdamanager.nodetype.NodeType): The nodetype
                looked-up.
        """
        logger.debug(
            "Looking up Node Manager NodeType for {definition}".format(
                definition=definition.nodeTypeName(),
            )
        )
        # namespace = utilities.node_type_namespace(
        #     definition.nodeTypeName(),
        # )
        repo = self.repo_from_definition(definition)
        logger.debug(
            "Repo {repo} found from definition {definition}".format(
                repo=repo,
                definition=definition.nodeTypeName(),
            )
        )

        if repo:
            current_name = definition.nodeTypeName()
            category = definition.nodeTypeCategory().name()
            index = utilities.node_type_index(current_name, category)
            return repo.node_types.get(index)

        logger.warning("No NodeType found.")
        return None

    def repo_from_definition(self, definition):
        """
        Retrieve the HDA repo the given definition belongs to.

        Args:
            definition(hou.HDADefinition): The definition to lookup the repo from.

        Returns:
            hda_repo(rbl_pipe_hdamanager.repo.HDARepo): The HDA repo instance for the
                given namespace.
        """
        logger.debug(
            "Looking up Node Manager Repo from definition: {definition}".format(
                definition=definition.nodeTypeName(),
            )
        )
        path = definition.libraryFilePath()
        repo = self.repo_from_hda_file(path)
        if repo:
            logger.info("Found repo from HDA file: {repo}".format(repo=repo))
            return repo
        logger.debug(
            "No repo found for definition after lookup based on filename: {path}".format(
                path=path,
            )
        )
        
        for repo_name in self.node_repos:
            repo = self.node_repos.get(repo_name)

        if repo:
            logger.warning("Defaulted to first repository found: {repo}".format(repo=repo))
            return repo
        
        logger.error(
            "No repo found for definition: {definition}".format(
                definition=definition,
            )
        )
        raise RuntimeError("No repo found for definition {definition}".format(definition=definition.nodeTypeName()))


    def repo_from_hda_file(self, path):
        """
        Retrieve the HDA repo the given filepath.

        Args:
            path(str): The path to lookup the repo from.

        Returns:
            hda_repo(rbl_pipe_hdamanager.repo.HDARepo): The HDA repo instance for the
                given namespace.
        """
        for repo_name in self.node_repos:
            repo = self.node_repos.get(repo_name)
            if path.startswith(repo.repo_root()):
                return repo
        return None
    
    def nodetypeversion_from_definition(self, definition):
        """
        Retrieve the nodetypeversion for the given definition.

        Args:
            definition(hou.HDADefinition): The definition to get the NodeTypeVersion
                for.

        Returns:
            node_type_version(rbl_pipe_hdamanager.nodetypeversion.NodeTypeVersion): The
                nodetype looked-up.
        """
        nodetype = self.nodetype_from_definition(definition)
        if nodetype:
            current_name = definition.nodeTypeName()
            version = utilities.node_type_version(current_name)
            return nodetype.versions.get(version)

        return None

    def is_latest_version(self, current_node):
        """
        Check if current node is the latest version.

        Args:
            current_node(hou.Node): The node to check the version for.

        Returns:
            (bool): Is the definition at the latest version.
        """
        definition = nodes.definition_from_node(current_node.path())

        # get all versions
        nodetype = self.nodetype_from_definition(definition)

        # If nodetype exists check that it is the latest version
        if nodetype:
            versions = [
                parse(version)
                for version
                in nodetype.all_versions().keys()
            ]
            versions_sorted = sorted(versions, reverse=True)
            latest_version = versions_sorted[0]

            # get current version
            nodeTypeName = definition.nodeTypeName()
            current_version = parse(utilities.node_type_version(nodeTypeName))

            # compare versions
            if current_version < latest_version:
                return False

        return True

    def edit_definition(self, current_node, major=False, minor=False):
        """Make a definition editable.

        Copy to our edit_dir with a unique name, and then add to the HDA
        manager and install to the current session.

        Args:
            current_node(hou.Node): The node to make the definition editable
            for.
            major(bool): Should the edit be a major version?
            minor(bool): Should the edit be a minor version?
        """
        if major and minor:
            raise RuntimeError("Can't edit definition as both major and minor.")

        definition = nodes.definition_from_node(current_node.path())

        dialog_message = (
            "You are about to edit a hda that is not the lastest version, do "
            "you want to continue?"
        )

        if not self.is_latest_version(current_node) and dialog.display_message(
            dialog_message, ("Ok", "Cancel"), title="Warning"
        ):
            logger.info("Making definition editable aborted by user.")
            return

        new_version = None
        if major or minor:
            logger.debug("Major or Minor version updated for editable node.")
            current_version = utilities.node_type_version(definition.nodeTypeName())
            current_version_components = len(current_version.split("."))
            version = parse(current_version)
            new_version = "{major}.{minor}".format(
                major=version.major + major,
                minor=version.minor + minor,
            )
            if current_version_components == 3:
                logger.debug(
                    "Current version is major.minor.patch, adding patch."
                )
                new_version = "{new_version}.{micro}".format(
                    new_version=new_version,
                    micro=version.micro,
                )

            logger.debug(
                "Editable node will be created with new version {version}".format(
                    version=new_version,
                )
            )

        # Copy and install definition modifying the nodetypename
        edit_repo = self.repo_from_definition(definition)
        updated_node_type_name = edit_repo.add_definition_copy(definition, version=new_version)

        if updated_node_type_name:
            # Update the node in the scene
            logger.debug(
                "Updating {node} to {name}".format(
                    node=current_node,
                    name=updated_node_type_name,
                )
            )
            current_node.changeNodeType(updated_node_type_name)

        # Clean up the old definition  if it wasn't part of repo
        definition_path = definition.libraryFilePath()
        repo = self.repo_from_hda_file(definition_path)
        if not repo:
            logger.debug("Unistalling {path}".format(path=definition_path))
            hou.hda.uninstallFile(definition.libraryFilePath())

    def prepare_publish(self, current_node):
        """
        Prepare a HDA publish using Pyblish.

        Args:
            current_node(hou.Node): The node we are attempting to publish from.
        """
        # # Make sure we don't already have plugins loaded from elsewhere
        # pyblish.api.deregister_all_paths()
        # pyblish.api.deregister_all_plugins()

        # # Make the node to be published available for collection
        # HDAManager.publish_node = current_node

        # # Register the application host
        # pyblish.api.register_host("houdini")

        # # Register the plugins
        # repo_root = os.path.abspath(__file__).rsplit("/lib/python", 1)[0]
        # plugins = "lib/python/rbl_pipe_hdamanager/pyblish_plugins"
        # pyblish.api.register_plugin_path(os.path.join(repo_root, plugins))

        # # Launch the UI
        # validator = houdinipyblishui.HoudiniPyblishUI(
        #     title="HDA Manager Validator",
        #     size=(800, 500),
        # )
        # HDAManager.validator_ui = validator.launch_ui()

        result = hou.ui.readInput(
            "Please enter a release comment for this node publish:",
            buttons=("Publish", "Cancel"),
            title="Node Manager: Publish Node",
        )
        if not result or result[0] == 1:
            logger.info("HDA Release cancelled by user.")
            return

        release_comment = None
        if result and result[1]:
            release_comment = result[1]

        repo = self.repo_from_definition(nodes.definition_from_node(current_node.path()))
        release_plugin = plugin.get_release_plugin(self.release_plugin, repo)
        if not release_plugin:
            raise RuntimeError("Couldn't find Node Manager Release Plugin.")

        return release_plugin.release(current_node, release_comment=release_comment)


def null_decorator(function):
    """A decorator that does nothing.

    Args:
        function(function): The function to decorate.
    """
    pass


def deferred_decorator(callback_returning_decorator):
    """ Borrowing from SideFX: $HFS/houdini/python3.9libs/sas/localassets.py
    This decorator defers another decorator from being called until the
    decorated function is actually called.

    Args:
        callback_returning_decorator(function): A function that returns the
            decorator to be used to decorate the function.

    Returns:
        function: The decorated function.
    """
    # We can't use the nonlocal keyword until Python 3, so use a mutable
    # object to let inner functions modify items local to the closure's
    # scope.
    if callback_returning_decorator() is None:
        return null_decorator

    closure_vars = {"decorated_function": None}

    def new_decorator(function):
        def wrapper(*args, **kwargs):
            decorated_function = closure_vars["decorated_function"]
            if decorated_function is None:
                # This is the first time the decorated function has been
                # called, so compute the actual decorated function and cache
                # it.
                decorator = callback_returning_decorator()
                decorated_function = decorator(function)
                closure_vars["decorated_function"] = decorated_function

            # Call the actual decorated function.
            return decorated_function(*args, **kwargs)
        return wrapper

    return new_decorator


@deferred_decorator(lambda: do_work_in_background_thread)
def initialise_in_background():
    """Initialise the Node Manager in the Houdini background thread."""
    logger.debug("Beginning initialisation using background thread.")
    yield
    manager_instance = NodeManager.init()
    manager_instance.load()
    yield
    logger.debug("Initialisation complete.")


def initialise_in_foreground():
    """Initialise the Node Manager in the Houdini main thread."""
    logger.debug("Beginning initialisation using main thread.")
    manager_instance = NodeManager.init()
    manager_instance.load()


def initialise_node_manager(background=True):
    """Initialise the Node Manager.

    Args:
        background(bool): Should the Node Manager be initialised in the
            background thread?
    """
    if background and not do_work_in_background_thread:
        logger.warning(
            "Attempted to use background thread but UI not available, "
            "reverting to main thread."
        )
    if background and do_work_in_background_thread:
        initialise_in_background()
    else:
        initialise_in_foreground()
