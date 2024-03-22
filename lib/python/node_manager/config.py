#!/usr/bin/env python

"""A very low-tech temp placeholder for a config."""


node_manager_config = {
    "background": False,
    "namespaces": [
        "{user}",
        "{user}.dev",
    ],
    "load_plugin": "GitLoad",
    "release_plugin": "GitRelease",
}
