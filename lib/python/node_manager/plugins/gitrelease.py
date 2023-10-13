#!/usr/bin/env python

import logging
import os
import subprocess
import time

from node_manager import release as node_release
from node_manager import utils
from node_manager import utilities
from node_manager.plugins import release

plugin_name = "GitRelease"
plugin_class = "release"
logger = logging.getLogger(
    "{plugin_class}.{plugin_name}".format(
        plugin_name=plugin_name,
        plugin_class=plugin_class,
    )
)


class NodeManagerPlugin(release.NodeManagerPlugin):
    name = plugin_name
    plugin_type = plugin_class

    def __init__(self, repo):
        """ 
        """
        super(NodeManagerPlugin, self).__init__(repo)
        logger.debug("Initialise Release.")

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
        #current_name = definition.nodeTypeName()
        #namespace = utilities.node_type_namespace(current_name)
        if self.repo:
            return self.repo.context.get("name")
        return None
        # repo = self.manager.repo_from_definition(definition)

        # if repo:
        #     return repo.name

        # return None

    def release_dir(self):
        """
        Get the path to the HDA edit release directory.

        Returns:
            (str): The release directory.
        """
        logger.debug(self.repo.context)
        return os.path.join(self.repo.context.get("git_repo_root"), "release")

    def release(self, current_node, release_comment=None):
        """
        Publish a definition being edited by the HDA manager.

        Args:
            current_node(hou.Node): The node to publish the definition for.
            release_comment(str, optional): The comment to use for the release.

        Raises:
            RuntimeError: HDA couldn't be expanded or package couldn't be found.
        """
        logger.info("Beginning HDA release.")

        # Get the release definitionq
        definition = self.get_release_definition(current_node)

        node_file_path = definition.libraryFilePath()
        if not release_comment:
            release_comment = "Updated {name}".format(
                name=utilities.node_type_name(node_file_path)
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

        repo = self.manager.repo_from_definition(definition)

        # Create and run the release
        hda_release = node_release.HDARelease(
            full_release_dir, node_type_name, branch, hda_name, package, release_comment, repo,
        )
        self.manager.releases.append(hda_release)
        released_path = hda_release.release()
        return

        # if not released_path:
        #     hou.ui.setStatusMessage(
        #         "HDA release aborted for {name}.".format(name=hda_name)
        #     )
        #     return

        # # Add newly released .hda
        # repo = self.repo_from_hda_file(released_path)
        # repo.process_hda_file(released_path, force=True)

        # # Remove released definition
        # repo.remove_definition(definition)

        # # Success
        # hou.ui.displayMessage(
        #     "HDA release successful!", title="HDA Manager: Publish HDA"
        # )
