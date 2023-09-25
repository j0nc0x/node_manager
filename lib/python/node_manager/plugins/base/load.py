import logging

logger = logging.getLogger(__name__)


class Load(object):
    plugin_type = "load"

    def __init__(self):
        """ 
        """
        logger.debug("Initialise Load.")

        self.extensions = [
            ".hda",
            ".hdanc",
            ".otl",
            ".otlnc",
        ]

    def load(self, path, root, temp):
        """Load the Node Manager repository.

        Args:
            path(str): The git path to the Node Manager repository.
            root(str): The root directory of the Node Manager repository.
            temp(str): The temp directory of the Node Manager repository.
        """
        raise NotImplementedError
