# -*- coding: utf-8 -*-

name = "node_manager"

version = "0.4.0"

description = "Houdini Node Manager"

authors = ["Jonathan Cox"]

requires = [
    "GitPython",
    "houdini",
    "packaging",
    "pyblish_lite", # Required for PyblishValidate plugin. Name dependent on local rez pyblish lite configuration.
    "python-3.11",
]

build_command = "{root}/bin/build {install}"

tests = {
    "unit": {
        "command": "export HOUDINI_PATH='&' && hython -m coverage run --source=node_manager -m pytest -vv tests && hython -m coverage report",
        "requires": [
            "pytest",
            "coverage",
            "importlib_metadata",
            "typing_extensions",
        ],
        "run_on": ["default", "pre_install", "pre_release"],
        "on_variants": True,
    }
}

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
