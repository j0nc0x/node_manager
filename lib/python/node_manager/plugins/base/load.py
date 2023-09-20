import logging

logger = logging.getLogger(__name__)


class Load(object):
    plugin_type = "load"

    def __init__(self):
        """ 
        """
        logger.debug("Initialise Load.")

    def load(self):
        """Implement this method to load a repositories contents.

        Returns:
            list: A list of Node Manager Repo objects.
        """
        raise NotImplementedError
