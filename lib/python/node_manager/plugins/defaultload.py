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

    def load(self):
        """Implement this method to load a repositories contents.
        """
        pass

