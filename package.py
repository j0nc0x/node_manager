# -*- coding: utf-8 -*-

name = "node_manager"

version = "0.2.1"

description = "Houdini Node Manager"

authors = ["Jonathan Cox"]

requires = [
    "GitPython",
    "houdini",
    "packaging",
]

build_command = "{root}/bin/build {install}"


def commands():
    env.PYTHONPATH.prepend("{root}/lib/python")

    # Note: '&' is used by Houdini to include the default locations for thse paths.
    # If this is handled elsewhere, either by a "houdini_config" rez package or the
    # Houdini rez package itself, then the '&' can be removed. See commented out lines
    # below which can be replaced.
    #env.HOUDINI_MENU_PATH.append("{root}/dcc/houdini/menu")
    #env.HOUDINI_PATH.append("{root}/dcc/houdini")
    env.HOUDINI_MENU_PATH.set("{root}/dcc/houdini/menu:&")
    env.HOUDINI_PATH.set("{root}/dcc/houdini:&")
