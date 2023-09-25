#!/usr/bin/env python

import logging
import sys

import hou

from node_manager import manager


logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    stream=sys.stdout,
)

manager.initialise_node_manager(background=hou.isUIAvailable())

# def houdini_startup():
#     """Houdini startup script.

#     Called when any of the Houdini executables is run.
#     """
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(levelname)s:[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
#         stream=sys.stdout,
#     )

#     # Set the default umask
#     repo_config = utils.get_config()
#     os.umask(repo_config.get("default_umask"))

#     # Set the correct frame rate
#     utils.set_frame_rate()

#     # Setup callback handler
#     hou.hipFile.addEventCallback(callbacks.handle_scene_callback)

#     HDAManager.init()