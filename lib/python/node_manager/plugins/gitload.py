import logging

logger = logging.getLogger(__name__)


from node_manager.plugins.base.load import Load

class NodeManagerPlugin(Load):
    name = "GitLoad"

    def __init__(self, manager):
        """ 
        """
        super(NodeManagerPlugin, self).__init__()
        self.manager = manager
        logger.debug("Initialsied GitLoad")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def load(self):
        """Implement this method to load a repositories contents.
        """
        pass

