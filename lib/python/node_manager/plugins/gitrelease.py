#!/usr/bin/env python

import json
import logging
import os
import re
import shutil
import subprocess
import time

from packaging.version import parse

import hou

from node_manager import utils
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

        self._release_dir = None
        self._node_type_name = None
        self._release_branch = None
        self._node_name = None
        self._release_version = None
        self._package = None
        self._comment = None
        self._repo = None

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
        #namespace = utils.node_type_namespace(current_name)
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
    


# #!/usr/bin/env python

# """HDA manager release process."""

# import json
# import logging
# import os
# import re
# import shutil

# from packaging.version import parse

# from git import Repo

# from node_manager import utils

# logger = logging.getLogger(__name__)


# class HDARelease(object):
#     """The HDA Release process.

#     This class handles the release process for a hou.HDADefinition that is ready to be
#     published. We ultimately want to have the option to run this outside of Houdini -
#     ie. on a server, so also want to avoid taking up a Houdini Engine license / running
#     the risk of not getting a license. Therefore all Houdini operations are complete
#     prior to this class being initialised.
#     """

#     # __config = get_config()
#     # hda_repo = __config.get("hda_repo")
#     hda_repo = "git@github.com:j0nc0x/hda_repo.git" # Read this from repo config to allow multiple git repositories
#     # package_root = "/Users/jcox/source/hda_library" # Read this from repo config to allow multiple git repositories

#     def __init__(
#         self,
#         release_dir,
#         node_type_name,
#         release_branch,
#         node_name,
#         package,
#         release_comment,
#         repo,
#     ):
#         """
#         Initialise HDARelease to prepare the release process.

#         Args:
#             release_dir(str): The working directory where the release will be run.
#             node_type_name(str): The node type name of the HDA being released.
#             release_branch(str): The branch to use for the release.
#             node_name(str): The name of the node being released.
#             package(str): The name of the package being released.
#             release_comment(str): The comment to use for the release.
#         """
#         self._release_dir = release_dir
#         self._node_type_name = node_type_name
#         self._release_branch = release_branch
#         self._node_name = node_name
#         self._release_version = None
#         self._package = package
#         self._comment = release_comment
#         self._repo = repo
#         logger.info("Initialised HDA Release process")
#         logger.debug("Release directory: {path}".format(path=self._release_dir))

    def _git_repo(self):
        return self._repo.context.get("git_repo")

    def _git_dir(self):
        """
        Get the path to the git repository.

        Returns:
            (str): The path to the git repository.
        """
        logger.debug(self._repo)
        logger.debug(self._repo.context)
        logger.debug(self._repo.context.get("git_repo_clone"))
        return self._repo.context.get("git_repo_clone")

    def _expand_dir(self):
        """
        Get the path where the HDA will be expanded.

        Returns:
            (str): The HDA expand directory.
        """
        return os.path.join(self._release_dir, self._node_name)

    def _node_root(self):
        """
        """
        return os.path.join(self._git_dir(), "dcc", "houdini", "hda")

    def _node_path(self):
        """
        Get the path to the node to be released.

        Returns:
            (str): The node path.
        """
        return os.path.join(self._node_root(), self._node_name)

    def _config_path(self):
        """
        """
        return os.path.join(self._git_dir(), "config", "config.json")

    def _generate_release_version(self, version, major, minor, patch):
        """
        """
        if major + minor + patch != 1:
            raise RuntimeError("Invalid version increment.")

        release_version = None
        parsed_version = parse(version)
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

    def _get_release_version(self, conf_version, major, minor, patch, release_tags):
        """
        """
        limit = 10
        i = 0
        release_version = self._generate_release_version(conf_version, major, minor, patch)
        while release_version in release_tags:
            i += 1
            release_version = self._generate_release_version(release_version, major, minor, patch)

            if i > limit:
                raise RuntimeError("Failed to generate release version after {iteration} iterations.".format(iteration=i))

        if i:
            logger.warning("Release version took {iteration} iterations to generate.".format(iteration=i + 1))

        return release_version

    def process_release(self):
        """
        Run the HDA release process.

        Returns:
            (str): The path of the released HDA.

        Raises:
            RuntimeError: The rez package released wasn't successful.
        """
        patch = False
        minor = False
        major = False

        config_path = self._config_path()

        # Create the branch
        current = self._git_repo().create_head(self._release_branch)
        current.checkout()

        # Check if expanded node directory already exists, delete it if it does
        hda_path = self._node_path()
        if os.path.exists(hda_path):
            patch = True
            shutil.rmtree(hda_path)
            logger.debug(
                "Removed directory already exists, removing: {path}".format(
                    path=hda_path
                )
            )
        else:
            namespace = utils.node_type_namespace(self._node_type_name)
            name = utils.node_type_name(self._node_type_name)
            version = utils.node_type_version(self._node_type_name)
            regex = re.compile(".*{namespace}\.{name}\.{major}\.(\d*).hda".format(namespace=namespace, name=name, major=parse(version).major))
            same_major_version = [path for path in os.listdir(self._node_root()) if regex.match(path)]
            if same_major_version:
                minor = True
            else:
                major = True

        repo_conf_data = {}
        with open(config_path, "r") as repo_conf:
            repo_conf_data = json.load(repo_conf)

        # Get the release version
        release_tags = [str(tag) for tag in self._git_repo().tags]
        self.release_version = self._get_release_version(repo_conf_data.get("version"), major, minor, patch, release_tags)

        # Copy the expanaded HDA into it's correct location
        shutil.copytree(self._expand_dir(), hda_path)

        # See if anything was updated
        changes = [change.a_path for change in self._git_repo().index.diff(None)]
        if not changes and not self._git_repo().untracked_files:
            logger.debug("No changes have been made to this HDA, aborting.")
            return None

        # Add and commit
        self._git_repo().git.add(A=True)
        self._git_repo().git.commit(m=self._comment)
        self._git_repo().git.push("--set-upstream", "origin", current)

        # Increment version in config
        repo_conf_data["version"] = self.release_version
        with open(config_path, "w") as repo_conf:
            json.dump(repo_conf_data, repo_conf)

        # Commit and push
        self._git_repo().git.commit(config_path, m="Version up")
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
        remote.push(refspec=(':{branch}'.format(branch=self._release_branch)))

        # clean up release dir
        #shutil.rmtree(self._release_dir)
        logger.debug(
            "(Would clean) up release directory {path}".format(path=self._release_dir)
        )

        # success
        logger.info("Release successful for {hda}.".format(hda=self._node_name))

        return True






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
        package = self.package_name_from_definition(definition)
        if not package:
            raise RuntimeError("No package found for definition")

        #repo = self.manager.repo_from_definition(definition)

        # Create and run the release
        # hda_release = node_release.HDARelease(
        #     full_release_dir, node_type_name, branch, hda_name, package, release_comment, self.repo,
        # )
        # self.manager.releases.append(hda_release)

        self._release_dir = full_release_dir
        self._node_type_name = node_type_name
        self._release_branch = branch
        self._node_name = hda_name
        self._release_version = None
        self._package = package
        self._comment = release_comment
        self._repo = self.repo

        return self.process_release()
