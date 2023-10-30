# -*- coding: utf-8 -*-

name = "node_manager"

version = "0.1.0"

description = "Houdini Node Manager"

authors = ["Jonathan Cox"]

requires = [
    "GitPython",
    "houdini",
    "packaging",
]

build_command = "python {root}/bin/build {install}"


def commands():
    env.PYTHONPATH.append("{root}/lib/python")
    env.HOUDINI_MENU_PATH.set("{root}/dcc/houdini/menu:&")
    env.HOUDINI_PATH.set("{root}/dcc/houdini:&")
    env.NODE_MANAGER_PLUGINS_PATH.append("{root}/lib/python/node_manager/plugins")
