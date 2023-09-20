import logging

logger = logging.getLogger(__name__)


class NodeManagerDiscover(object):
    plugin_type = "NodeManagerDiscover"

    def __init__(self):
        """ 
        """
        logger.debug("Initialise NodeManagerDiscover.")

    def discover(self):
        """Implement this method to discover any node repositories that should
        be loaded.

        Returns:
            list: A list of Node Manager Repo objects.
        """
        raise NotImplementedError
