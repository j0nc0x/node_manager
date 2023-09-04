#!/usr/bin/env python

"""HDA manager release process."""

import logging
import os
import shutil

from git import Repo

logger = logging.getLogger(__name__)


class HDARelease(object):
    """The HDA Release process.

    This class handles the release process for a hou.HDADefinition that is ready to be
    published. We ultimately want to have the option to run this outside of Houdini -
    ie. on a server, so also want to avoid taking up a Houdini Engine license / running
    the risk of not getting a license. Therefore all Houdini operations are complete
    prior to this class being initialised.
    """

    # __config = get_config()
    # hda_repo = __config.get("hda_repo")
    hda_repo = "git@github.com:j0nc0x/hda_repo.git" # Read this from repo config to allow multiple git repositories
    # package_root = "/Users/jcox/source/hda_library" # Read this from repo config to allow multiple git repositories

    def __init__(
        self,
        release_dir,
        node_type_name,
        release_branch,
        node_name,
        package,
        release_comment,
    ):
        """
        Initialise HDARelease to prepare the release process.

        Args:
            release_dir(str): The working directory where the release will be run.
            node_type_name(str): The node type name of the HDA being released.
            release_branch(str): The branch to use for the release.
            node_name(str): The name of the node being released.
            package(str): The name of the package being released.
            release_comment(str): The comment to use for the release.
        """
        self.release_dir = release_dir
        self.node_type_name = node_type_name
        self.release_branch = release_branch
        self.node_name = node_name
        self.release_version = None
        self.package = package
        self.comment = release_comment
        logger.info("Initialised HDA Release process")

    def git_dir(self):
        """
        Get the path to the git repository.

        Returns:
            (str): The path to the git repository.
        """
        return os.path.join(self.release_dir, "git")

    def expand_dir(self):
        """
        Get the path where the HDA will be expanded.

        Returns:
            (str): The HDA expand directory.
        """
        return os.path.join(self.release_dir, self.node_name)

    def node_path(self):
        """
        Get the path to the node to be released.

        Returns:
            (str): The node path.
        """
        return os.path.join(self.git_dir(), "dcc", "houdini", "hda", self.node_name)

    def release(self):
        """
        Run the HDA release process.

        Returns:
            (str): The path of the released HDA.

        Raises:
            RuntimeError: The rez package released wasn't successful.
        """
        # Clone the repo
        cloned_repo = Repo.clone_from(self.hda_repo, self.git_dir())

        current = cloned_repo.create_head(self.release_branch)
        current.checkout()

        # Check if expanded node directory already exists, delete it if it does
        hda_path = self.node_path()
        if os.path.exists(hda_path):
            shutil.rmtree(hda_path)
            logger.debug(
                "Removed directory already exists, removing: {path}".format(
                    path=hda_path
                )
            )

        # Copy the expanaded HDA into it's correct location
        shutil.copytree(self.expand_dir(), hda_path)

        # See if anything was updated
        changes = [change.a_path for change in cloned_repo.index.diff(None)]
        if not changes and not cloned_repo.untracked_files:
            logger.debug("No changes have been made to this HDA, aborting.")
            return None

        # Add and commit
        cloned_repo.git.add(A=True)
        cloned_repo.git.commit(m=self.comment)
        cloned_repo.git.push("--set-upstream", "origin", current)

    #     # Up the package version
    #     fh, abs_path = mkstemp()
    #     with os.fdopen(fh, "w") as new_file:
    #         with open(self.package_py_path()) as old_file:
    #             for line in old_file:
    #                 if line.startswith("version"):
    #                     versions = re.findall('"([^"]*)"', line)
    #                     if len(versions) != 1:
    #                         raise RuntimeError(
    #                             "Invalid package.py. Found {num} version strings. "
    #                             "Should only be one.".format(num=len(versions))
    #                         )

    #                     version = parse(versions[0])
    #                     self.release_version = "{major}.{minor}.{patch}".format(
    #                         major=version.major, minor=version.minor + 1, patch=0
    #                     )
    #                     updated_line = 'version = "{version}"\n'.format(
    #                         version=self.release_version
    #                     )
    #                     new_file.write(updated_line)
    #                 else:
    #                     new_file.write(line)

    #     shutil.copymode(self.package_py_path(), abs_path)
    #     os.remove(self.package_py_path())
    #     shutil.move(abs_path, self.package_py_path())

    #     # Commit and push
    #     cloned_repo.git.commit(self.package_py_path(), m="Version up")
    #     cloned_repo.git.push()

    #     # rez-release
    #     subprocess_env = rezclean.get_base_env()
    #     # In case we're operating in a custom Rez environment:
    #     subprocess_env["REZ_CONFIG_FILE"] = os.getenv("REZ_CONFIG_FILE")
    #     process = subprocess.Popen(
    #         "rez-release",
    #         cwd=self.package_root(),
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         env=subprocess_env,
    #     )
    #     process.wait()

    #     # verify release
    #     if process.returncode != 0:
    #         # Non-zero return code
    #         try:
    #             _stdout = process.stdout.read()
    #             _stderr = process.stderr.read()
    #         except Exception as e:
    #             _stdout = ""
    #             _stderr = str(e)
    #         raise RuntimeError(
    #             "rez-release didn't complete successfully: {} :: {} :: {}".format(
    #                 process.returncode, _stdout, _stderr
    #             )
    #         )

    #     release_path = self.release_hda_path()
    #     # Using open instead of os.path.exists as we seemed to be getting false
    #     # negatives with that approach - caching issue perhaps.
    #     try:
    #         with os.path.open(release_path, "r") as fh:
    #             pass
    #         exists = True
    #     except Exception:
    #         exists = False
    #     if exists:
    #         raise RuntimeError(
    #             "Error when verifying the release, expected to find released hda at: "
    #             "{path}".format(path=release_path)
    #         )

        # merge to master
        cloned_repo.git.reset("--hard")
        main = cloned_repo.heads.main
        main.checkout()
        cloned_repo.git.pull()
        cloned_repo.git.merge(current, "--no-ff")
        cloned_repo.git.push()

        # clean up release dir
        #shutil.rmtree(self.release_dir)
        logger.debug(
            "(Would clean) up release directory {path}".format(path=self.release_dir)
        )

        # success
        logger.info("Release successful for {hda}.".format(hda=self.node_name))

        return True
