import logging

logger = logging.getLogger(__name__)

from node_manager import utils
from node_manager.plugins.base.load import Load

class NodeManagerPlugin(Load):
    name = "DefaultLoad"

    def __init__(self):
        """Initialise the DefaultLoad plugin."""
        super(NodeManagerPlugin, self).__init__()
        self.manager = utils.get_manager()
        logger.debug("Initialsied DefaultLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def load(self, path, root, temp):
        """Load the Node Manager repository.

        Args:
            path(str): The path to the Node Manager repository.
            root(str): The root directory of the Node Manager repository.
            temp(str): The temp directory of the Node Manager repository.
        """
        pass
