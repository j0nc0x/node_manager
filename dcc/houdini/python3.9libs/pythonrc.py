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

# # Disk based load
# os.environ["NODE_MANAGER_REPOS"] = "/Users/jcox/hdas"
# os.environ["NODE_MANAGER_BASE"] = "/Users/jcox/hdas"
# manager.initialise_node_manager(
#     background=hou.isUIAvailable(),
#     edit_plugin="EditDirectory",
# )

# Git based load
os.environ["NODE_MANAGER_REPOS"] = "git@github.com:j0nc0x/hda_repo.git"
# os.environ["NODE_MANAGER_BASE"] = "/Users/jcox/hdas_git"
manager.initialise_node_manager(
    background=hou.isUIAvailable(),
    load_plugin="GitLoad",
    edit_plugin="EditDirectory",
    release_plugin="GitRelease",
)
