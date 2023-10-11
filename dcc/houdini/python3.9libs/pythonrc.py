#!/usr/bin/env python

import logging
import os
import sys

import hou

from node_manager import manager


logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    stream=sys.stdout,
)

# os.environ["NODE_MANAGER_BASE"] = "/Users/jcox/hdas"
# manager.initialise_node_manager(
#     background=hou.isUIAvailable(),
# )

os.environ["NODE_MANAGER_BASE"] = "/Users/jcox/hdas_git"
manager.initialise_node_manager(
    background=hou.isUIAvailable(),
    load_plugin="GitLoad",
    release_plugin="GitRelease",
)
