import logging

logger = logging.getLogger(__name__)


from node_manager.nodemanagerstore import NodeManagerStore

class NodeManagerPlugin(NodeManagerStore):
    name = "DefaultNodeManagerStore"

    def __init__(self):
        """ 
        """
        logger.debug("Initialsied DefaultStore")
        logger.debug(self.name)
        logger.debug(self.plugin_type)

    def load(self):
        """
        """
        pass

    def publish(self):
        """
        """
        pass