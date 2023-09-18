import logging

logger = logging.getLogger(__name__)


class NodeManagerStore(object):
    plugin_type = "NodeManagerStore"

    def __init__(self):
        """ 
        """
        logger.debug("Initialise NodeManagerStore.")