#!/usr/bin/env python

"""Start the Node Manager."""

import logging
import sys

from node_manager import manager


def initialise():
    """Initialise the Node Manager."""
    # Setting up logging here, but this can be skipped if it is handled elsewhere.
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s:[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        stream=sys.stdout,
    )

    # Initialise the Node Manager
    manager.initialise_node_manager()
