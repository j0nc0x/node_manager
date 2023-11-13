#!/usr/bin/env python

import json
import logging
import os
import re
import shutil
import subprocess
import time
from tempfile import mkstemp

from packaging.version import parse

import hou

from node_manager import utils
from node_manager.plugins import release

plugin_name = "RezRelease"
plugin_class = "release"
logger = logging.getLogger(
    "{plugin_class}.{plugin_name}".format(
        plugin_name=plugin_name,
        plugin_class=plugin_class,
    )
)


class NodeManagerPlugin(release.NodeManagerPlugin):
    """Git Release Plugin."""

    name = plugin_name
    plugin_type = plugin_class

    def __init__(self):
        """Initialise the RezRelease plugin."""
        super(NodeManagerPlugin, self).__init__()

        self._release_dir = None
        self._node_type_name = None
        self.node_name = None

        logger.debug("Initialise Release.")

    def package_name(self):
        """
        Lookup the package name from the context.

        Returns:
            (str): The package name.
        """
        if self.repo:
            name = self.repo.context.get("name")
            return name.split(".")[0]
        return None

    def release_dir(self):
        """
        Get the path to the HDA edit release directory.

        Returns:
            (str): The release directory.
        """
        logger.debug(self.repo.context)
        return os.path.join(self.repo.context.get("git_repo_root"), "release")

    def _git_repo(self):
        """Get the git repository.

        Returns:
            (git.Repo): The git repository.
        """
        return self.repo.context.get("git_repo")

    def _git_dir(self):
        """
        Get the path to the git repository.

        Returns:
            (str): The path to the git repository.
        """
        return self.repo.context.get("git_repo_clone")

    def _expand_dir(self):
        """
        Get the path where the HDA will be expanded.

        Returns:
            (str): The HDA expand directory.
        """
        return os.path.join(self._release_dir, self.node_name)

    def _node_root(self):
        """Get the path to the node root.

        Returns:
            (str): The path to the node root.
        """
        return os.path.join(self._git_dir(), "dcc", "houdini", "hda")

    def _node_path(self):
        """
        Get the path to the node to be released.

        Returns:
            (str): The node path.
        """
        return os.path.join(self._node_root(), self.node_name)

    def _config_path(self):
        """Get the path to the config file.
        
        Returns:
            (str): The path to the config file.
        """
        return os.path.join(self._git_dir(), "config", "config.json")

    def version_from_package(self):
        if os.path.isfile(self.package_py_path()):
            old_package_py_path = self.package_py_path()
        else:
            old_package_py_path = os.path.join(os.environ.get("REZ_NODE_MANAGER_ROOT"), "data", "default_package.py")

        logger.debug("Using package.py: {path}".format(path=old_package_py_path))

        with open(old_package_py_path) as old_file:
            for line in old_file:
                if line.startswith("version"):
                    versions = re.findall('"([^"]*)"', line)
                    if len(versions) != 1:
                        raise RuntimeError(
                            "Invalid package.py. Found {num} version strings. "
                            "Should only be one.".format(num=len(versions))
                        )

                    return versions[0]

        raise RuntimeError("Couldn't find version in package.py")

    def process_release(self, definition, branch, package_name, comment=None):
        """
        Run the HDA release process.

        Args:
            definition(hou.HDADefinition): The definition to release.
            branch(str): The name of the branch to release to.
            package_name(str): The name of the package to release to.
            comment(str, optional): The comment to use for the release.

        Returns:
            (str): The path of the released HDA.

        Raises:
            RuntimeError: The rez package released wasn't successful.
        """
        config_path = self._config_path()

        # Create the branch
        current = self._git_repo().create_head(branch)
        current.checkout()

        # Check if expanded node directory already exists, delete it if it does
        hda_path = self._node_path()
        if os.path.exists(hda_path):
            shutil.rmtree(hda_path)
            logger.debug(
                "Removed directory already exists, removing: {path}".format(
                    path=hda_path
                )
            )

        repo_conf_data = {}
        if os.path.isfile(config_path):
            with open(config_path, "r") as repo_conf:
                repo_conf_data = json.load(repo_conf)
        else:
            logger.warning("No config found at {path}, skipping.".format(path=config_path))

        package_version = self.version_from_package()

        # Get the release version
        self.release_version = self.manager.get_release_version(definition, package_version)

        # Copy the expanaded HDA into it's correct location
        shutil.copytree(self._expand_dir(), hda_path)

        # See if anything was updated
        changes = [change.a_path for change in self._git_repo().index.diff(None)]
        if not changes and not self._git_repo().untracked_files:
            logger.debug("No changes have been made to this HDA, aborting.")
            return None

        # Add and commit
        self._git_repo().git.add(A=True)
        self._git_repo().git.commit(m=comment)
        self._git_repo().git.push("--set-upstream", "origin", current)

        # Up the package version
        fh, abs_path = mkstemp()
        with os.fdopen(fh, "w") as new_file:
            if os.path.isfile(self.package_py_path()):
                old_package_py_path = self.package_py_path()
            else:
                old_package_py_path = os.path.join(os.environ.get("REZ_NODE_MANAGER_ROOT"), "data", "default_package.py")

            logger.debug("Using package.py: {path}".format(path=old_package_py_path))

            with open(old_package_py_path) as old_file:
                for line in old_file:
                    if line.startswith("version"):
                        updated_line = 'version = "{version}"\n'.format(
                            version=self.release_version
                        )
                        new_file.write(updated_line)
                    elif "<name>" in line:
                        new_file.write(line.replace("<name>", package_name))
                    elif "<description>" in line:
                        new_file.write(line.replace("<description>", "Node Manager repo {package_name}".format(package_name=package_name)))
                    else:
                        new_file.write(line)

        # Move the new package.py into place
        if os.path.exists(self.package_py_path()):
            #shutil.copymode(self.package_py_path(), abs_path)
            os.remove(self.package_py_path())
        shutil.move(abs_path, self.package_py_path())

        # Commit and push
        self._git_repo().git.add(A=True)
        self._git_repo().git.commit(self.package_py_path(), m="Version up")
        self._git_repo().git.push()

        # Push tag to repo
        new_tag = self._git_repo().create_tag(self.release_version, message="Release {version}".format(version=self.release_version))
        self._git_repo().remotes.origin.push(new_tag)

        # merge to master
        self._git_repo().git.reset("--hard")
        main = self._git_repo().heads.main
        main.checkout()
        self._git_repo().git.pull()
        self._git_repo().git.merge(current, "--no-ff")
        self._git_repo().git.push()

        # remove release branch
        remote = self._git_repo().remote(name='origin')
        remote.push(refspec=(':{branch}'.format(branch=branch)))

        # clean up release dir
        #shutil.rmtree(self._release_dir)
        logger.debug(
            "(Would clean) up release directory {path}".format(path=self._release_dir)
        )

        # success
        logger.info("Release successful for {hda}.".format(hda=self.node_name))

        return True

    def release(self, current_node, release_comment=None):
        """
        Publish a definition being edited by the HDA manager.

        Args:
            current_node(hou.Node): The node to publish the definition for.
            release_comment(str, optional): The comment to use for the release.

        Raises:
            RuntimeError: HDA couldn't be expanded or package couldn't be found.

        Returns:
            bool: Was the release successful.
        """
        logger.info("Beginning HDA release.")

        # Get the release definitionq
        definition = self.get_release_definition(current_node)

        node_file_path = definition.libraryFilePath()
        if not release_comment:
            release_comment = "Updated {name}".format(
                name=utils.node_type_name(node_file_path)
            )

        # Define the release directory
        release_subdir = "release_{time}".format(time=int(time.time()))
        full_release_dir = os.path.join(self.release_dir(), release_subdir)

        # Expand the HDA ready for release
        hda_name = utils.expanded_hda_name(definition)
        expand_dir = os.path.join(full_release_dir, hda_name)

        # expandToDirectory doesn't allow inclusion of contents - raise with SideFx, but
        # reverting to subprocess.
        cmd = [
            "hotl",
            "-x" if hou.isApprentice() else "-tp", # Maybe we should error-check this?
            expand_dir,
            definition.libraryFilePath(),
        ]
        process = subprocess.Popen(cmd)
        process.wait()

        # verify release
        if process.returncode != 0:
            # Non-zero return code
            raise RuntimeError("HDA expansion didn't complete successfully.")

        # Determine the other information needed to conduct a release
        node_type_name = definition.nodeTypeName()
        branch = utils.release_branch_name(definition)
        package = self.package_name()
        if not package:
            raise RuntimeError("No package found for definition")
        logger.debug("Using package: {package}".format(package=package))

        self._release_dir = full_release_dir
        self._node_type_name = node_type_name
        self.node_name = hda_name

        return self.process_release(definition, branch, package, comment=release_comment)

        # # rez-release
        # subprocess_env = rezclean.get_base_env()
        # # In case we're operating in a custom Rez environment:
        # subprocess_env["REZ_CONFIG_FILE"] = os.getenv("REZ_CONFIG_FILE")
        # process = subprocess.Popen(
        #     "rez-release",
        #     cwd=self.package_root(),
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     env=subprocess_env,
        # )
        # process.wait()

        # # verify release
        # if process.returncode != 0:
        #     # Non-zero return code
        #     try:
        #         _stdout = process.stdout.read()
        #         _stderr = process.stderr.read()
        #     except Exception as e:
        #         _stdout = ""
        #         _stderr = str(e)
        #     raise RuntimeError(
        #         "rez-release didn't complete successfully: {} :: {} :: {}".format(
        #             process.returncode, _stdout, _stderr
        #         )
        #     )

        # release_path = self.release_hda_path()
        # # Using open instead of os.path.exists as we seemed to be getting false
        # # negatives with that approach - caching issue perhaps.
        # try:
        #     with os.path.open(release_path, "r") as fh:
        #         pass
        #     exists = True
        # except Exception:
        #     exists = False
        # if exists:
        #     raise RuntimeError(
        #         "Error when verifying the release, expected to find released hda at: "
        #         "{path}".format(path=release_path)
        #     )

        # # merge to master
        # cloned_repo.git.reset("--hard")
        # master = cloned_repo.heads.master
        # master.checkout()
        # cloned_repo.git.pull()
        # cloned_repo.git.merge(current, "--no-ff")
        # cloned_repo.git.push()

        # # clean up release dir
        # shutil.rmtree(self.release_dir)
        # logger.debug(
        #     "Cleaned up release directory {path}".format(path=self.release_dir)
        # )

        # # success
        # logger.info("Release successful for {hda}.".format(hda=self.hda_name))

        # return self.release_hda_path()

    def package_py_path(self):
        """
        Get the path to the package.py file.

        Returns:
            (str): The path to the package.py file.
        """
        return os.path.join(self._git_dir(), "package.py")