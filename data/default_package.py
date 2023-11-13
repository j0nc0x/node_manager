name = "<name>"

description = "<description>"

version = "0.0.0"

authors = [
    ]

requires = [
    "houdini",
    "node_manager",
]

def commands():
    env.NODE_MANAGER_REPOS.prepend("{root}/dcc/houdini/hdas")

build_command = "{root}/install.py  --root={root} --install={install}"
