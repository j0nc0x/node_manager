import logging
import os

from node_manager import repo
from node_manager import utils

logger = logging.getLogger(__name__)


from node_manager.plugins.base.discover import Discover

class NodeManagerPlugin(Discover):
    name = "DefaultDiscover"

    def __init__(self):
        """Initialise the DefaultDiscover plugin."""
        super(NodeManagerPlugin, self).__init__()
        self.manager = utils.get_manager()
        logger.debug("Initialsied DefaultDiscover")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    @staticmethod
    def get_repo_paths():
        """Get a list of Node Manager repository paths from the environment.

        Returns:
            (list): A list of Node Manager repositories in the current environment.
        """
        repo_paths = []
        node_manage_repos = os.getenv("NODE_MANAGER_REPOS")
        if node_manage_repos:
            repo_paths = node_manage_repos.split(",")
        return repo_paths

    def discover(self):
        """Initialise Node Repositories from the NODE_MANAGER_REPOS environment
        variable.

        Returns:
            list: A list of Node Manager Repo objects.
        """
        node_repos = {}
        for path in self.get_repo_paths():
            # Create the repository object
            node_repo = repo.NodeRepo(self.manager, path)
            name = node_repo.get_name()

            # Add to repositories list
            node_repos[name] = node_repo

        return node_repos
