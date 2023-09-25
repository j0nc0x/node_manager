import logging
import os
import subprocess

logger = logging.getLogger(__name__)

from node_manager import utils
from node_manager.plugins.base.load import Load

from git import Repo
from git.exc import NoSuchPathError, InvalidGitRepositoryError


class NodeManagerPlugin(Load):
    name = "GitLoad"

    def __init__(self):
        """Initialise the GitLoad plugin."""
        super(NodeManagerPlugin, self).__init__()
        self.manager = utils.get_manager()
        self.git_repo = None
        logger.debug("Initialsied GitLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def clone_repo(self, repo_path, root):
        """Clone the Node Manager repository."""
        cloned_repo = None
        try:
            cloned_repo = Repo(root)
            cloned_repo.git.pull()
        except (NoSuchPathError, InvalidGitRepositoryError) as error:
            logger.debug("Couldn't load repo from {path}, clone instead.".format(path=root))

        if not cloned_repo:
            cloned_repo = Repo.clone_from(repo_path, root, depth=1)

        return cloned_repo

    def build_repo(self, root, temp):
        """Build the Node Manager repository."""
        os.makedirs(temp)
        expanded_hda_dir = os.path.join(root, "dcc", "houdini", "hda")
        for hda in os.listdir(expanded_hda_dir):
            path = os.path.join(expanded_hda_dir, hda)
            hda_path = os.path.join(temp, hda)
            logger.info("Processing {source}".format(source=path))
            hotl_cmd = ["hotl", "-C", path, hda_path]
            logger.debug(hotl_cmd)
            result = subprocess.call(hotl_cmd)

    def load(self, repo_path, root, temp):
        """Load the Node Manager repository."""
        self.git_repo = self.clone_repo(repo_path, root)
        self.build_repo(root, temp)
