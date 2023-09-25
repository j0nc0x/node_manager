#!/usr/bin/env python

"""HDA manager."""

import getpass
import logging
import os
import pkgutil
import subprocess
import time

from tempfile import mkdtemp

import hou

if hou.isUIAvailable():
    from hdefereval import do_work_in_background_thread
else:
    do_work_in_background_thread = None

from node_manager import release
from node_manager import repo
from node_manager import utilities
from node_manager.utils import plugin

from node_manager.dependencies import nodes

logger = logging.getLogger(__name__)


class NodeManager(object):
    """Main HDA Manager Class."""

    instance = None
    plugin_path = "/Users/jcox/source/github/node_manager/lib/python/node_manager/plugins" # Read from env var
    discover_plugin = None
    load_plugin = "GitLoad"
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
        self._plugins = plugin.import_plugins(self.plugin_path)

        self.temp_dir = mkdtemp(prefix="node-manager-")
        self.base = self.get_base()
        self.edit_dir = self.setup_edit_dir()

        self.setup_callbacks()

        self.releases = list()
    #     self.depth = int(os.getenv("HDA_MANAGER_LOAD_DEPTH", 5))

    #     self.configure_window = None

        self.node_repos = self.initialise_repos()
        start = time.time()
        self.load_all()
        self.stats["load_hdas"] = time.time() - start

        print(self.stats)

    def initialise_repos(self):
        discover_plugin = plugin.get_discover_plugin(self.discover_plugin)
        if not discover_plugin:
            raise RuntimeError("Couldn't find Node Manager Discover Plugin.")

        return discover_plugin.discover()

    def save(self, current_node):
        definition = current_node.type().definition()
        save_path = definition.libraryFilePath()
        install = False
        if save_path.startswith(self.temp_dir):
            logger.info("Saving HDA to node manager edit directory.")
            hda_filename = os.path.basename(save_path)
            save_path = os.path.join(self.edit_dir, hda_filename)
            install = True

        definition.updateFromNode(current_node)
        definition.save(save_path)

        if install:
            hou.hda.installFile(
                save_path,
                oplibraries_file="Scanned Asset Library Directories",
                force_use_assets=True,
            )

    def save_hda_callback(self, asset_definition, **kwargs):
        print("before save HDA")
        print(asset_definition)
        print(kwargs)

    def setup_callbacks(self):
        """
        """
        hou.hda.addEventCallback((hou.hdaEventType.BeforeAssetSaved, ), self.save_hda_callback)

    def is_initialised(self):
        """
        """
        return self.initialised

    def get_base(self):
        base = os.getenv("NODE_MANAGER_BASE")
        if not base:
            base = self.temp_dir
            os.environ["NODE_MANAGER_BASE"] = self.temp_dir
        return base

    def setup_edit_dir(self):
        """
        """
        edit_dir = os.path.join(self.base, "edit", getpass.getuser())
        os.makedirs(edit_dir, exist_ok=True)
        return edit_dir

    def load_all(self):
        """Load all nodeTypes."""
        for repo_name in self.node_repos:
            self.node_repos.get(repo_name).load_nodes()

    def repo_from_definition(self, definition):
        """
        Retrieve the HDA repo the given definition belongs to.

        Args:
            definition(hou.HDADefinition): The definition to lookup the repo from.

        Returns:
            hda_repo(rbl_pipe_hdamanager.repo.HDARepo): The HDA repo instance for the
                given namespace.
        """
        path = definition.libraryFilePath()
        return self.repo_from_hda_file(path)

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

    def package_name_from_definition(self, definition):
        """
        Use the namespace for the given definition to infer the rez package.

        Args:
            definition(hou.HDADefinition): The definition to work out the package name
                from.

        Returns:
            (str): The package name.

        Raises:
            RuntimeError: No package could be found based on the given definition.
        """
        # if utilities.allow_show_publish():
        #     repo = self.repo_from_project()

        #     if repo:
        #         return repo.package_name

        #     raise RuntimeError("No package found for the current project")
        # else:
        current_name = definition.nodeTypeName()
        #namespace = utilities.node_type_namespace(current_name)
        repo = self.repo_from_definition(definition)

        if repo:
            return repo.name

        return None

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

        self.publish_definition(current_node)

    def publish_definition(self, current_node):
        """
        Publish a definition being edited by the HDA manager.

        Args:
            current_node(hou.Node): The node to publish the definition for.

        Returns:
            (None)

        Raises:
            RuntimeError: HDA couldn't be expanded or package couldn't be found.
        """
        result = hou.ui.readInput(
            "Please enter a release comment for this node publish:",
            buttons=("Publish", "Cancel"),
            title="Node Manager: Publish Node",
        )
        if not result or result[0] == 1:
            logger.info("HDA Release cancelled by user.")
            return

        definition = nodes.definition_from_node(current_node.path())
        definition.updateFromNode(current_node)

        current_name = definition.libraryFilePath()
        if result[1]:
            release_comment = result[1]
        else:
            release_comment = "Updated {name}".format(
                name=utilities.node_type_name(current_name)
            )

        # Define the release directory
        release_subdir = "release_{time}".format(time=int(time.time()))
        full_release_dir = os.path.join(self.release_dir(), release_subdir)

        # Expand the HDA ready for release
        hda_name = utilities.expanded_hda_name(definition)
        expand_dir = os.path.join(full_release_dir, hda_name)

        # expandToDirectory doesn't allow inclusion of contents - raise with SideFx, but
        # reverting to subprocess.
        cmd = ["hotl", "-X", expand_dir, definition.libraryFilePath()]
        process = subprocess.Popen(cmd)
        process.wait()

        # verify release
        if process.returncode != 0:
            # Non-zero return code
            raise RuntimeError("HDA expansion didn't complete successfully.")

        # Determine the other information needed to conduct a release
        node_type_name = definition.nodeTypeName()
        branch = utilities.release_branch_name(definition)
        package = self.package_name_from_definition(definition)
        if not package:
            raise RuntimeError("No package found for definition")

        repo = self.repo_from_definition(definition)

        # Create and run the release
        hda_release = release.HDARelease(
            full_release_dir, node_type_name, branch, hda_name, package, release_comment, repo,
        )
        print(hda_release)
        self.releases.append(hda_release)
        released_path = hda_release.release()
        print(released_path)
        return

        if not released_path:
            hou.ui.setStatusMessage(
                "HDA release aborted for {name}.".format(name=hda_name)
            )
            return

        # Add newly released .hda
        repo = self.repo_from_hda_file(released_path)
        repo.process_hda_file(released_path, force=True)

        # Remove released definition
        repo.remove_definition(definition)

        # Success
        hou.ui.displayMessage(
            "HDA release successful!", title="HDA Manager: Publish HDA"
        )

def null_decorator(function):
    pass


def deferred_decorator(callback_returning_decorator):
    """ Borrowing this from SideFX -> $HFS/houdini/python3.9libs/sas/localassets.py
    This decorator defers another decorator from being called until the
    decorated function is actually called.
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
    logger.debug("Beginning initialisation using background thread.")
    yield
    manager_instance = NodeManager.init()
    manager_instance.load()
    yield
    logger.debug("Initialisation complete.")

def initialise_in_foreground():
    logger.debug("Beginning initialisation using main thread.")
    manager_instance = NodeManager.init()
    manager_instance.load()

def initialise_node_manager(background=True):
    if background and not do_work_in_background_thread:
        logger.warning("Attempted to use background thread but UI not available, reverting to main thread.")
    if background and do_work_in_background_thread:
        initialise_in_background()
    else:
        initialise_in_foreground()
