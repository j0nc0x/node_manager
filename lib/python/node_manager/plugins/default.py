import logging

logger = logging.getLogger(__name__)


from node_manager.nodemanagerstore import NodeManagerStore

class NodeManagerPlugin(NodeManagerStore):
    name = "DefaultNodeManagerStore"

    def __init__(self):
        """ 
        """
        logger.info("Initialsied DefaultStore")
        logger.info(self.name)
        logger.info(self.plugin_type)

    def load(self):
        """
        """
        pass

    def publish(self):
        """
        """
        pass