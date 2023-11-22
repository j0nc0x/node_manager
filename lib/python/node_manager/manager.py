#!/usr/bin/env python

"""HDA manager."""

import getpass
import logging
import os
import time

from tempfile import mkdtemp

import hou

from packaging.version import parse

if hou.isUIAvailable():
    from hdefereval import do_work_in_background_thread
else:
    do_work_in_background_thread = None

from node_manager import utils
from node_manager.utils import plugin
from node_manager.utils import callbacks
from node_manager.utils import definition as definitionutils
from node_manager.utils import nodes
from node_manager.utils import nodetypeutils

logger = logging.getLogger(__name__)


class NodeManager(object):
    """Main HDA Manager Class."""

    instance = None

    @classmethod
    def init(
        cls,
        discover_plugin=None,
        load_plugin=None,
        edit_plugin=None,
        release_plugin=None,
    ):
        """
        Initialise the HDAManager if it isn't already initialised, storing the instance in the class.

        Args:
            discover_plugin(str, optional): The name of the discover plugin to use.
            load_plugin(str, optional): The name of the load plugin to use.
            edit_plugin(str, optional): The name of the edit plugin to use.
            release_plugin(str, optional): The name of the release plugin to use.

        Returns:
            (HDAManager): The HDAManager instance.
        """
        if cls.instance is None:
            start = time.time()
            cls.instance = cls(
                discover_plugin=discover_plugin,
                load_plugin=load_plugin,
                edit_plugin=edit_plugin,
                release_plugin=release_plugin,
            )
            cls.instance.stats["init"] = time.time() - start
        return cls.instance

    def __init__(
        self,
        discover_plugin=None,
        load_plugin=None,
        edit_plugin=None,
        release_plugin=None,
    ):
        """Initialise the NodeManager class.

        Args:
            discover_plugin(str, optional): The name of the discover plugin to use.
            load_plugin(str, optional): The name of the load plugin to use.
            edit_plugin(str, optional): The name of the edit plugin to use.
            release_plugin(str, optional): The name of the release plugin to use.
        """
        logger.info("Initialising Node Manager")

        self.node_repos = {}

        # Define which plugins to use.
        self.discover_plugin = discover_plugin
        self.load_plugin = load_plugin
        self.edit_plugin = edit_plugin
        self.release_plugin = release_plugin

        self.stats = {}

    def load(self):
        """Load the HDA Manager."""
        self._plugins = plugin.import_plugins()

        self.context = {}
        self.context["manager_temp_dir"] = mkdtemp(prefix="node-manager-")
        self.context["manager_base_dir"] = self.get_base_dir()
        self.context["manager_edit_dir"] = self.get_edit_dir()
        self.context["manager_backup_dir"] = os.path.join(self.context.get("manager_edit_dir"), "backup")
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
            base_dir = self.context.get("manager_temp_dir")
            os.environ["NODE_MANAGER_BASE"] = self.context.get("manager_temp_dir")
        return base_dir

    def get_edit_dir(self, create_on_disk=True):
        """Get the edit directory for the HDA Manager.

        Args:
            create_on_disk(bool): Should the directory be created on disk if
                it doesn't exist?

        Returns:
            str: The edit directory for the HDA Manager.
        """
        edit_dir = os.path.join(self.context.get("manager_base_dir"), "edit", getpass.getuser())
        if create_on_disk:
            os.makedirs(edit_dir, exist_ok=True)
        return edit_dir

    def git_dir(self):
        """
        """
        return os.path.join(self.context.get("manager_temp_dir"), "git")

    def load_all(self, force=False):
        """Load all node definitions from the repositories."""
        for repo_name in self.node_repos:
            node_repo = self.node_repos.get(repo_name)
            node_repo.initialise_repo()
            node_repo.load_nodes(force=force)

    def is_node_manager_node(self, current_node, compare_path=True):
        """Check if the given node is a Node Manager node.

        Args:
            current_node(hou.Node): The node to check.
            compare_path(bool, optional): Should the node path be used as an additional check?

        Returns:
            (bool): Is the node a Node Manager node?
        """
        # We can reject nodes straight away if they are not digital assets.
        if not nodes.is_digital_asset(current_node.path()):
            return False

        definition = nodes.definition_from_node(current_node.path())
        if not definition:
            raise RuntimeError("Couldn't find definition for {node}".format(node=current_node))
        
        nodetypeversion = self.nodetypeversion_from_definition(definition)
        logger.debug("Nodetypeversion: {nodetypeversion}".format(nodetypeversion=nodetypeversion))
        if not nodetypeversion:
            logger.debug("{node} is not a Node Manager node.".format(node=current_node))
            return False

        # If we are not comparing the library file path then we can consider this a match
        if not compare_path:
            logger.debug("{node} is a Node Manager node.".format(node=current_node))
            return True

        # Otherwise lets compare the definition paths on disk
        matched_definitions = [version  for version in nodetypeversion if version.definition.libraryFilePath() == definition.libraryFilePath()]
        if matched_definitions:
            logger.debug("{node} is a Node Manager node.".format(node=current_node))
            return True
        else:
            logger.debug("{node} is not a Node Manager node.".format(node=current_node))
            return False

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
            version = nodetypeutils.node_type_version(current_name)
            return nodetype.versions.get(version)

        return None

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
            index = utils.node_type_index(current_name, category)
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
        
        # for repo_name in self.node_repos:
        #     repo = self.node_repos.get(repo_name)

        # if repo:
        #     logger.warning("Defaulted to first repository found: {repo}".format(repo=repo))
        #     return repo
        
        # logger.error(
        #     "No repo found for definition: {definition}".format(
        #         definition=definition,
        #     )
        # )
        # raise RuntimeError("No repo found for definition {definition}".format(definition=definition.nodeTypeName()))


    def repo_from_hda_file(self, path):
        """
        Retrieve the HDA repo the given filepath.

        Args:
            path(str): The path to lookup the repo from.

        Returns:
            hda_repo(rbl_pipe_hdamanager.repo.HDARepo): The HDA repo instance for the
                given namespace.
        """
        logger.debug("Checking if {path} is in a repo.".format(path=path))
        for repo_name in self.node_repos:
            repo = self.node_repos.get(repo_name)
            logger.debug("Checking repo with path: {path}".format(path=repo.context))
            if path.startswith(repo.context.get("repo_load_path")):
                return repo
        return None

    def get_release_repo(self):
        """Get the release repository for the given node.

        Returns:
            node_manager.repo.NodeRepo: The release repository.

        Raises:
            NotImplementedError: Multiple repo support not currently implemented.
            RuntimeError: No repos found.
        """
        if len(self.node_repos) > 1:
            raise NotImplementedError("Multiple repo support not currently implemented.")

        if self.node_repos:
            return next(iter(self.node_repos.values()))

        raise RuntimeError("No repos found.")

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
            current_version = parse(nodetypeutils.node_type_version(nodeTypeName))

            # compare versions
            if current_version < latest_version:
                return False

        return True

    def get_release_version(self, definition, package_version):
        """
        Get the release version for the given definition.

        Args:
            definition(hou.HDADefinition): The definition to get the release
                version for.
            package_version(str): The package version to use as a base.

        Returns:
            str: The release version.

        Raises:
            RuntimeError: Invalid version increment.
        """
        major = False
        minor = False
        patch = False

        release_repo = self.get_release_repo()
        current_name = definition.nodeTypeName()
        category = definition.nodeTypeCategory().name()
        index = utils.node_type_index(current_name, category)
        current_version = nodetypeutils.node_type_version(current_name)
        nodetype = release_repo.node_types.get(index)
        if nodetype:
            version = nodetype.versions.get(current_version)
            if version:
                patch = True
                logger.debug("Version exists - patch release.")
            else:
                same_major_version = [version for version in nodetype.versions if version.startswith(current_version.split(".")[0])]
                if same_major_version:
                    minor = True
                    logger.debug("Same major version - minor release.")
                else:
                    major = True
                    logger.debug("Different major version - major release.")
        else:
            logger.debug("New node type - major release.")
            major = True

        if major + minor + patch != 1:
            raise RuntimeError("Invalid version increment.")

        release_version = None
        parsed_version = parse(package_version)
        if patch:
            release_version = "{major}.{minor}.{patch}".format(
                major=parsed_version.major,
                minor=parsed_version.minor,
                patch=parsed_version.micro + 1,
            )
        elif minor:
            release_version = "{major}.{minor}.{patch}".format(
                major=parsed_version.major,
                minor=parsed_version.minor + 1,
                patch=0,
            )
        elif major:
            release_version = "{major}.{minor}.{patch}".format(
                major=parsed_version.major + 1,
                minor=0,
                patch=0,
            )

        return release_version

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
        path = current_node.path()
        logger.debug(
            "Edit {node} (Major: {major}, Minor: {minor})".format(
                node=current_node,
                major=major,
                minor=minor,
            )
        )
        if major and minor:
            raise RuntimeError("Can't edit definition as both major and minor.")

        edit_plugin = plugin.get_edit_plugin(self.edit_plugin)
        if not edit_plugin:
            raise RuntimeError("Couldn't find Node Manager Edit Plugin.")

        edit_plugin.edit_definition(current_node, major=major, minor=minor)

        # Force node callback to run
        callbacks.node_changed(nodes.node_at_path(path))

    def discard_definition(self, current_node):
        """
        Discard a definition being edited by the HDA manager.

        Args:
            current_node(hou.Node): The node we are attempting to discard.

        Raises:
            RuntimeError: Cant discard from read-only HDA repo.
        """    
        if not self.is_node_manager_node(current_node):
            # Uninstall the definition
            definition = nodes.definition_from_node(current_node.path())
            definitionutils.uninstall_definition(
                definition, backup_dir=self.context.get("backup_dir")
            )

            # Force node callback to run
            callbacks.node_changed(current_node)
        else:
            raise RuntimeError("Can't discard definition from NodeManager HDA repo.")

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
        path = current_node.path()

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

        release_plugin = plugin.get_release_plugin(self.release_plugin)
        if not release_plugin:
            raise RuntimeError("Couldn't find Node Manager Release Plugin.")

        success = release_plugin.release(current_node, release_comment=release_comment)

        if success:
            self.load_all(force=True)
            callbacks.node_changed(nodes.node_at_path(path))

            # # Add newly released .hda
            # repo = self.manager.repo_from_hda_file(released_path)
            # repo.process_hda_file(released_path, force=True)

            # # Remove released definition
            # repo.remove_definition(definition)

            # Success
            utils.display_message(
                "HDA release successful!", title="HDA Manager: Publish HDA"
            )



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
def initialise_in_background(
    discover_plugin=None,
    load_plugin=None,
    edit_plugin=None,
    release_plugin=None,
):
    """Initialise the Node Manager in the Houdini background thread.

    Args:
        discover_plugin(str, optional): The name of the discover plugin to use.
        load_plugin(str, optional): The name of the load plugin to use.
        edit_plugin(str, optional): The name of the edit plugin to use.
        release_plugin(str, optional): The name of the release plugin to use.
    """
    logger.debug("Beginning initialisation using background thread.")
    yield
    manager_instance = NodeManager.init(
        discover_plugin=discover_plugin,
        load_plugin=load_plugin,
        edit_plugin=edit_plugin,
        release_plugin=release_plugin,
    )
    manager_instance.load()
    yield
    logger.debug("Initialisation complete.")


def initialise_in_foreground(
    discover_plugin=None,
    load_plugin=None,
    edit_plugin=None,
    release_plugin=None,
):
    """Initialise the Node Manager in the Houdini main thread.

    Args:
        discover_plugin(str, optional): The name of the discover plugin to use.
        load_plugin(str, optional): The name of the load plugin to use.
        edit_plugin(str, optional): The name of the edit plugin to use.
        release_plugin(str, optional): The name of the release plugin to use.
    """
    logger.debug("Beginning initialisation using main thread.")
    manager_instance = NodeManager.init(
        discover_plugin=discover_plugin,
        load_plugin=load_plugin,
        edit_plugin=edit_plugin,
        release_plugin=release_plugin,
    )
    manager_instance.load()


def initialise_node_manager(
        background=True,
        discover_plugin=None,
        load_plugin=None,
        edit_plugin=None,
        release_plugin=None,
    ):
    """Initialise the Node Manager.

    Args:
        background(bool): Should the Node Manager be initialised in the
            background thread?
        discover_plugin(str, optional): The name of the discover plugin to use.
        load_plugin(str, optional): The name of the load plugin to use.
        edit_plugin(str, optional): The name of the edit plugin to use.
        release_plugin(str, optional): The name of the release plugin to use.
    """
    logger.debug(
        "Initialising Node Manager using discover plugin: {discover_plugin}, "
        "load_plugin: {load_plugin}, edit_plugin: {edit_plugin}, release_plugin: {release_plugin}.".format(
            discover_plugin=discover_plugin,
            load_plugin=load_plugin,
            edit_plugin=edit_plugin,
            release_plugin=release_plugin,
        )
    )
    if background and not do_work_in_background_thread:
        logger.warning(
            "Attempted to use background thread but UI not available, "
            "reverting to main thread."
        )
    if background and do_work_in_background_thread:
        initialise_in_background(
            discover_plugin=discover_plugin,
            load_plugin=load_plugin,
            edit_plugin=edit_plugin,
            release_plugin=release_plugin,
        )
    else:
        initialise_in_foreground(
            discover_plugin=discover_plugin,
            load_plugin=load_plugin,
            edit_plugin=edit_plugin,
            release_plugin=release_plugin,
        )
