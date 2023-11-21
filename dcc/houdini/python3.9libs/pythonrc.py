#!/usr/bin/env python

import logging
import os
import sys

import hou

from node_manager import manager
from node_manager import utils


logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    stream=sys.stdout,
)


if utils.using_rez():
    manager.initialise_node_manager(
        background=hou.isUIAvailable(),
        load_plugin="RezLoad",
        release_plugin="RezRelease",
    )
else:
    os.environ["NODE_MANAGER_PLUGINS_PATH"] = "/Users/jcox/source/github/node_manager/lib/python/node_manager/plugins"

    # # Disk based load
    # os.environ["NODE_MANAGER_REPOS"] = "/Users/jcox/hdas"
    # os.environ["NODE_MANAGER_BASE"] = "/Users/jcox/hdas"
    # manager.initialise_node_manager(
    #     background=hou.isUIAvailable(),
    # )

    # Git based load
    os.environ["NODE_MANAGER_REPOS"] = "git@github.com:j0nc0x/hda_repo.git"
    manager.initialise_node_manager(
        background=hou.isUIAvailable(),
        load_plugin="GitLoad",
        release_plugin="GitRelease",
    )