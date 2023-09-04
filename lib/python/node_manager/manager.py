#!/usr/bin/env python

"""HDA manager."""

import logging
import os
import subprocess
import time

from tempfile import mkdtemp

import hou

from node_manager import release
from node_manager import repo
from node_manager import utilities

from node_manager.dependencies import nodes

logger = logging.getLogger(__name__)


class NodeManager(object):
    """Main HDA Manager Class."""

    instance = None
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
            cls.instance = cls()
        return cls.instance

    def __init__(
        self,
    ):
        """Initialise the NodeManager class."""
        logger.info("Initialising Node Manager")
        self.node_repos = dict()
        self.releases = list()
    #     self.depth = int(os.getenv("HDA_MANAGER_LOAD_DEPTH", 5))
        self.edit_dir = self.edit_dir()

    #     self.configure_window = None

        self.initialise_repositories()
        self.load_all()

    def get_repo_paths(self):
        """
        Get a list of Node Manager repository paths from the environment.

        Returns:
            (list): A list of Node Manager repositories in the current environment.
        """
        repo_paths = []
        node_manage_repos = os.getenv("NODE_MANAGER_HOUDINI")
        if node_manage_repos:
            repo_paths = node_manage_repos.split(os.pathsep)

        return repo_paths

    def edit_dir(self):
        """
        """
        return mkdtemp(prefix="node-manager-")

    def release_dir(self):
        """
        Get the path to the HDA edit release directory.

        Returns:
            (str): The release directory.
        """
        return os.path.join(self.edit_dir, "release")

    def initialise_repositories(self):
        """Initialise the HDA repoositories."""
        # # Create the repository object
        # editable_hda_repo = repo.HDARepo(self, self.edit_dir, editable=True)
        # name = editable_hda_repo.get_name()
        # # Add to repositories list
        # self.hda_repos[name] = editable_hda_repo

        # Loop over all repositories by looking at NODE_MANAGER_HOUDINI env var
        repo_paths = self.get_repo_paths()
        for path in repo_paths:
            # Create the repository object
            node_repo = repo.NodeRepo(self, path)
            name = node_repo.get_name()

            # Add to repositories list
            self.node_repos[name] = node_repo

    def load_all(self):
        """Load all nodeTypes."""
        for repo_name in self.node_repos:
            self.node_repos.get(repo_name).load()

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
            return repo.package_name

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

        # Create and run the release
        hda_release = release.HDARelease(
            full_release_dir, node_type_name, branch, hda_name, package, release_comment
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
