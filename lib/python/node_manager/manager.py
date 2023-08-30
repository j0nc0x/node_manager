#!/usr/bin/env python

"""HDA manager."""

import logging
import os
# import subprocess
# import time

# import hou

# from packaging.version import parse

# import pyblish.api

# from rbl_pipe_hdamanager import history
# from rbl_pipe_hdamanager import release
from node_manager import repo
# from rbl_pipe_hdamanager import ui
# from rbl_pipe_hdamanager import utilities

# from rbl_pipe_houdini.pyblish import houdinipyblishui
# from rbl_pipe_houdini.utils import dialog
# from rbl_pipe_houdini.utils import nodes

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
    #     self.releases = list()
    #     self.depth = int(os.getenv("HDA_MANAGER_LOAD_DEPTH", 5))
    #     # Using $HOME for now - probably need to think about testing on the farm, as
    #     # nodes edited in this location won't be available.
    #     self.edit_dir = os.path.join(hou.homeHoudiniDirectory(), "otls/hdamanager")

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

    # def backup_dir(self):
    #     """
    #     Get the path to the HDA edit backup directory.

    #     Returns:
    #         (str): The backup directory.
    #     """
    #     return os.path.join(self.edit_dir, "backup")

    # def release_dir(self):
    #     """
    #     Get the path to the HDA edit release directory.

    #     Returns:
    #         (str): The release directory.
    #     """
    #     return os.path.join(self.edit_dir, "release")

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

    # def load_all_from_scene(self):
    #     """Load any nodeTypes that are required by the current scene.

    #     This will only consider nodeTypes that aren't already loaded.
    #     """
    #     all_nodes = hou.root().allSubChildren()
    #     all_types = list(
    #         set(
    #             [
    #                 node.type()
    #                 for node in all_nodes
    #                 if nodes.definition_from_node(node.path())
    #             ]
    #         )
    #     )

    #     for node_type in all_types:
    #         definition = node_type.definition()
    #         current_name = definition.nodeTypeName()
    #         namespace = utilities.node_type_namespace(current_name)
    #         name = utilities.node_type_name(current_name)
    #         version = utilities.node_type_version(current_name)
    #         category = definition.nodeTypeCategory().name()
    #         nodetypeversions = (
    #             self.nodetypeversion_from_category_namespace_name_and_version(
    #                 category, namespace, name, version
    #             )
    #         )
    #         if nodetypeversions:
    #             for nodetypeversion in nodetypeversions:
    #                 if not nodetypeversion.installed:
    #                     nodetypeversion.install_definition()

    # def all_available_namespaces(self, filter_pipeline=True):
    #     """
    #     Generate a list of all possible namespaces based on the loaded HDA repos.

    #     Args:
    #         filter_pipeline(:obj:`bool`,optional): Should the pipeline repo be filtered
    #             out.

    #     Returns:
    #         all_namespaces(list): A list of all available namespaces.
    #     """
    #     all_namespaces = list()
    #     for repo_name in self.hda_repos:
    #         hda_repo = self.hda_repos.get(repo_name)
    #         # Filter out the pipeline HDAs depending on user / config
    #         if (
    #             filter_pipeline
    #             and not utilities.allow_pipeline()
    #             and hda_repo.get_name() == "houdini_hdas_pipeline"
    #         ):
    #             continue
    #         all_namespaces.extend(hda_repo.available_namespaces())

    #     return all_namespaces

    # def valid_namespace(self, definition):
    #     """
    #     Check if the namespace is valid for the given definition.

    #     Args:
    #         definition(hou.HDADefinition): The definition we wish to check the namespace
    #             validity for.

    #     Returns:
    #         (bool): Is the namespace valid?
    #     """
    #     hda_package = self.package_name_from_definition(definition)
    #     if not hda_package:
    #         return False
    #     elif hda_package == "houdini_hdas_pipeline":
    #         return utilities.allow_pipeline()
    #     return True

    # def repo_from_definition(self, definition):
    #     """
    #     Retrieve the HDA repo the given definition belongs to.

    #     Args:
    #         definition(hou.HDADefinition): The definition to lookup the repo from.

    #     Returns:
    #         hda_repo(rbl_pipe_hdamanager.repo.HDARepo): The HDA repo instance for the
    #             given namespace.
    #     """
    #     path = definition.libraryFilePath()
    #     return self.repo_from_hda_file(path)

    # def repo_from_hda_file(self, path):
    #     """
    #     Retrieve the HDA repo the given filepath.

    #     Args:
    #         path(str): The path to lookup the repo from.

    #     Returns:
    #         hda_repo(rbl_pipe_hdamanager.repo.HDARepo): The HDA repo instance for the
    #             given namespace.
    #     """
    #     for repo_name in self.hda_repos:
    #         repo = self.hda_repos.get(repo_name)
    #         if path.startswith(repo.repo_root()):
    #             return repo
    #     return None

    # def repo_from_namespace(self, namespace):
    #     """
    #     Given a namespace, lookup the rbl_pipe_hdamanager.repo.HDARepo.

    #     Args:
    #         namespace(str): The namespace to lookup the repo from.

    #     Returns:
    #         hda_repo(rbl_pipe_hdamanager.repo.HDARepo): The HDA repo instance for the
    #             given namespace.
    #     """
    #     for repo_name in self.hda_repos:
    #         hda_repo = self.hda_repos.get(repo_name)
    #         if namespace in hda_repo.available_namespaces():
    #             return hda_repo
    #     return None

    # def nodetype_from_definition(self, definition, include_editable=True):
    #     """
    #     Retrieve the nodetype for the given definition.

    #     Args:
    #         definition(hou.HDADefinition): The HDA definition to use when
    #             looking up the HDA Manager nodetype.
    #         include_editable(:obj:`bool`,optional): Should we allow lookups into the
    #             editable repo.

    #     Returns:
    #         node_type(rbl_pipe_hdamanager.nodetype.NodeType): The nodetype looked-up.
    #     """
    #     # Look-up the repo from the definition. How we do this depends on if we
    #     # want to include the editable repo when doing this.
    #     if include_editable:
    #         repo = self.repo_from_definition(definition)
    #     else:
    #         namespace = utilities.node_type_namespace(
    #             definition.nodeTypeName(),
    #         )
    #         repo = self.repo_from_namespace(namespace)

    #     if repo:
    #         current_name = definition.nodeTypeName()
    #         category = definition.nodeTypeCategory().name()
    #         index = utilities.node_type_index(current_name, category)
    #         return repo.node_types.get(index)

    #     return None

    # def nodetype_from_category_namespace_and_name(
    #     self, category, namespace, name, project_repo=False
    # ):
    #     """Get the NodeType.

    #     Given a hou.nodeType category, namespace and name, lookup the
    #     rbl_pipe_hdamanager.nodetype.NodeType.

    #     Args:
    #         category(str): The node type category to lookup.
    #         namespace(str): The node type namespace to lookup.
    #         name(str): The node type name to lookup.
    #         project_repo(:obj:`bool`,optional): Use the project repo, other than the one
    #             defined by the namespace.

    #     Returns:
    #         node_type(rbl_pipe_hdamanager.nodetype.NodeType): The nodetype looked-up.
    #     """
    #     if project_repo:
    #         repo = self.repo_from_project()
    #     else:
    #         repo = self.repo_from_namespace(namespace)
    #     node_type = None
    #     if repo:
    #         index = utilities.node_type_index_from_components(namespace, name, category)
    #         node_type = repo.node_types.get(index)

    #     return node_type

    # def repo_from_project(self):
    #     """
    #     Return the HDA repo for the current project.

    #     Returns:
    #         repo(rbl_pipe_hdamanager.repo.HDARepo): The project HDA repo.
    #     """
    #     project = os.getenv("RBL_PROJECT")
    #     repo_name = "houdini_hdas_{project}".format(project=project)
    #     return self.hda_repos.get(repo_name)

    # def nodetypeversion_from_definition(self, definition):
    #     """
    #     Retrieve the nodetypeversion for the given definition.

    #     Args:
    #         definition(hou.HDADefinition): The definition to get the NodeTypeVersion
    #             for.

    #     Returns:
    #         node_type_version(rbl_pipe_hdamanager.nodetypeversion.NodeTypeVersion): The
    #             nodetype looked-up.
    #     """
    #     nodetype = self.nodetype_from_definition(definition)
    #     if nodetype:
    #         current_name = definition.nodeTypeName()
    #         version = utilities.node_type_version(current_name)
    #         return nodetype.versions.get(version)

    #     return None

    # def nodetypeversion_from_category_namespace_name_and_version(
    #     self, category, namespace, name, version
    # ):
    #     """Get the NodeTypeVersion.

    #     Given a hou.nodeType category, namespace, name and version, lookup the
    #     rbl_pipe_hdamanager.nodetypeversion.NodeTypeVersion.

    #     Args:
    #         category(str): The node type category to lookup.
    #         namespace(str): The node type namespace to lookup.
    #         name(str): The node type name to lookup.
    #         version(str): The node type version to lookup.

    #     Returns:
    #         node_type_version(rbl_pipe_hdamanager.nodetypeversion.NodeTypeVersion): The
    #             nodetype looked-up.
    #     """
    #     node_type = self.nodetype_from_category_namespace_and_name(
    #         category, namespace, name
    #     )
    #     node_type_version = None
    #     if node_type:
    #         node_type_version = node_type.versions.get(version)

    #     return node_type_version

    # def package_name_from_definition(self, definition):
    #     """
    #     Use the namespace for the given definition to infer the rez package.

    #     Args:
    #         definition(hou.HDADefinition): The definition to work out the package name
    #             from.

    #     Returns:
    #         (str): The package name.

    #     Raises:
    #         RuntimeError: No package could be found based on the given definition.
    #     """
    #     if utilities.allow_show_publish():
    #         repo = self.repo_from_project()

    #         if repo:
    #             return repo.package_name

    #         raise RuntimeError("No package found for the current project")
    #     else:
    #         current_name = definition.nodeTypeName()
    #         namespace = utilities.node_type_namespace(current_name)
    #         repo = self.repo_from_namespace(namespace)

    #         if repo:
    #             return repo.package_name

    #         return None

    # def add_hda_file(self, path):
    #     """
    #     Add the given HDA file to the relevant repo.

    #     Args:
    #         path(str): The HDA file path.
    #     """
    #     repo = self.repo_from_hda_file(path)
    #     repo.process_hda_file(path, force=True)

    # def current_node_type_version(self, category, namespace, name):
    #     """
    #     Get the current verson for the given nodetype namespace and name.

    #     Args:
    #         category(str): The node type category.
    #         namespace(str): The node type namespace.
    #         name(str): The node type name.

    #     Returns:
    #         (str): The current version of the definition.
    #     """
    #     nodetype = self.nodetype_from_category_namespace_and_name(
    #         category, namespace, name
    #     )
    #     versions = []
    #     if nodetype:
    #         versions = [parse(version) for version in nodetype.versions.keys()]

    #     # Also need to consider any HDAs that have been released to the current project
    #     # but using the same namespace.
    #     project_nodetype = self.nodetype_from_category_namespace_and_name(
    #         category, namespace, name, project_repo=True
    #     )
    #     if project_nodetype:
    #         versions += [parse(version) for version in project_nodetype.versions.keys()]

    #     if not versions:
    #         return None

    #     versions.sort()
    #     return str(versions[-1])

    # def is_latest_version(self, current_node):
    #     """
    #     Check if current node is the latest version.

    #     Args:
    #         current_node(hou.Node): The node to check the version for.

    #     Returns:
    #         (bool): Is the definition at the latest version.
    #     """
    #     definition = nodes.definition_from_node(current_node.path())

    #     # get all versions
    #     nodetype = self.nodetype_from_definition(definition, include_editable=False)

    #     # If nodetype exists check that it is the latest version
    #     if nodetype:
    #         versions = [parse(version) for version in nodetype.all_versions().keys()]
    #         versions_sorted = sorted(versions, reverse=True)
    #         latest_version = versions_sorted[0]

    #         # get current version
    #         nodeTypeName = definition.nodeTypeName()
    #         current_version = parse(utilities.node_type_version(nodeTypeName))

    #         # compare versions
    #         if current_version < latest_version:
    #             return False

    #     return True

    # def edit_definition(self, current_node):
    #     """Make a definition editable.

    #     Copy to our edit_dir with a unique name, and then add to the HDA manager and
    #     install to the current session.

    #     Args:
    #         current_node(hou.Node): The node to make the definition editable for.

    #     Returns:
    #         (None)
    #     """
    #     definition = nodes.definition_from_node(current_node.path())

    #     dialog_message = (
    #         "You are about to edit a hda that is not the lastest version, do you want "
    #         "to continue?"
    #     )

    #     if not self.is_latest_version(current_node) and dialog.display_message(
    #         dialog_message, ("Ok", "Cancel"), title="Warning"
    #     ):
    #         logger.info("Making definition editable aborted by user.")
    #         return

    #     edit_repo = self.hda_repos.get("editable")
    #     edit_repo.add_definition_copy(definition)

    # def discard_definition(self, current_node):
    #     """
    #     Discard a definition being edited by the HDA manager.

    #     Args:
    #         current_node(hou.Node): The node we are attempting to discard.

    #     Raises:
    #         RuntimeError: Cant pubish from read-only HDA repo.
    #     """
    #     definition = nodes.definition_from_node(current_node.path())

    #     repo = self.repo_from_definition(definition)
    #     if repo.get_name() != "editable":
    #         raise RuntimeError("Can only discard a defintion from the editable repo")

    #     repo.remove_definition(definition)

    # def configure_definition(self, current_node):
    #     """
    #     Configure a definiton being edited by the HDA manager.

    #     Args:
    #         current_node(hou.Node): The node we are attempting to configure.
    #     """
    #     self.configure_window = ui.ConfigureWindow(self, current_node)
    #     self.configure_window.show()

    # def prepare_publish(self, current_node):
    #     """
    #     Prepare a HDA publish using Pyblish.

    #     Args:
    #         current_node(hou.Node): The node we are attempting to publish from.
    #     """
    #     # Make sure we don't already have plugins loaded from elsewhere
    #     pyblish.api.deregister_all_paths()
    #     pyblish.api.deregister_all_plugins()

    #     # Make the node to be published available for collection
    #     HDAManager.publish_node = current_node

    #     # Register the application host
    #     pyblish.api.register_host("houdini")

    #     # Register the plugins
    #     repo_root = os.path.abspath(__file__).rsplit("/lib/python", 1)[0]
    #     plugins = "lib/python/rbl_pipe_hdamanager/pyblish_plugins"
    #     pyblish.api.register_plugin_path(os.path.join(repo_root, plugins))

    #     # Launch the UI
    #     validator = houdinipyblishui.HoudiniPyblishUI(
    #         title="HDA Manager Validator",
    #         size=(800, 500),
    #     )
    #     HDAManager.validator_ui = validator.launch_ui()

    # def publish_definition(self, current_node):
    #     """
    #     Publish a definition being edited by the HDA manager.

    #     Args:
    #         current_node(hou.Node): The node to publish the definition for.

    #     Returns:
    #         (None)

    #     Raises:
    #         RuntimeError: HDA couldn't be expanded or package couldn't be found.
    #     """
    #     result = hou.ui.readInput(
    #         "Please enter a release comment for this HDA publish:",
    #         buttons=("Publish", "Cancel"),
    #         title="HDA Manager: Publish HDA",
    #     )
    #     if not result or result[0] == 1:
    #         logger.info("HDA Release cancelled by user.")
    #         return

    #     definition = nodes.definition_from_node(current_node.path())
    #     definition.updateFromNode(current_node)

    #     current_name = definition.libraryFilePath()
    #     if result[1]:
    #         release_comment = result[1]
    #     else:
    #         release_comment = "Updated {name}".format(
    #             name=utilities.node_type_name(current_name)
    #         )

    #     # Define the release directory
    #     release_subdir = "release_{time}".format(time=int(time.time()))
    #     full_release_dir = os.path.join(self.release_dir(), release_subdir)

    #     # Expand the HDA ready for release
    #     hda_name = utilities.expanded_hda_name(definition)
    #     expand_dir = os.path.join(full_release_dir, hda_name)

    #     # expandToDirectory doesn't allow inclusion of contents - raise with SideFx, but
    #     # reverting to subprocess.
    #     cmd = ["hotl", "-X", expand_dir, definition.libraryFilePath()]
    #     process = subprocess.Popen(cmd)
    #     process.wait()

    #     # verify release
    #     if process.returncode != 0:
    #         # Non-zero return code
    #         raise RuntimeError("HDA expansion didn't complete successfully.")

    #     # Determine the other information needed to conduct a release
    #     node_type_name = definition.nodeTypeName()
    #     branch = utilities.release_branch_name(definition)
    #     package = self.package_name_from_definition(definition)
    #     if not package:
    #         raise RuntimeError("No package found for definition")

    #     # Create and run the release
    #     hda_release = release.HDARelease(
    #         full_release_dir, node_type_name, branch, hda_name, package, release_comment
    #     )
    #     self.releases.append(hda_release)
    #     released_path = hda_release.release()

    #     if not released_path:
    #         hou.ui.setStatusMessage(
    #             "HDA release aborted for {name}.".format(name=hda_name)
    #         )
    #         return

    #     # Add newly released .hda
    #     repo = self.repo_from_hda_file(released_path)
    #     repo.process_hda_file(released_path, force=True)

    #     # Remove released definition
    #     repo.remove_definition(definition)

    #     # Success
    #     hou.ui.displayMessage(
    #         "HDA release successful!", title="HDA Manager: Publish HDA"
    #     )

    # def release_history(self, current_node):
    #     """
    #     Show the release history.

    #     Args:
    #         current_node(hou.Node): The node to display the release history for.
    #     """
    #     hda_history = history.HDAHistory(current_node, self)
    #     hda_history.release_history()
