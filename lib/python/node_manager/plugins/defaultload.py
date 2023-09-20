import logging

logger = logging.getLogger(__name__)


from node_manager.plugins.base.load import Load

class NodeManagerPlugin(Load):
    name = "DefaultLoad"

    def __init__(self, manager):
        """ 
        """
        super(NodeManagerPlugin, self).__init__()
        self.manager = manager
        logger.debug("Initialsied DefaultLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def load(self):
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
