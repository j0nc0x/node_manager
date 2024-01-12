# Node Manager
Manage and track Houdini HDAs (and in the future, Nuke Gizmos/Snippets).

## Design
Key design factors include:
- Should feel like the user is just referencing node definitions from a directory on disk. Minimise extra steps.
- All node changes tracked through source control.
- Use standard UIs and workflows where possible.

Further design considerations [here](docs/design.md).

## Requirements
General Requirements:
- `packaging`: https://pypi.org/project/packaging/

For Git/Rez Load/Release:
- `GitPython`: https://pypi.org/project/GitPython/

For Rez Load/Release:
- `rez`: https://github.com/AcademySoftwareFoundation/rez

## Install NodeManager
### Rez
The preferred installation method is through [rez](https://github.com/AcademySoftwareFoundation/rez). In order to deploy with rez:
- Clone this repository.
- Make any site specific updates to the `package.py`.
- Configure `NodeManager` using the config (see below).
- Build using `rez-build -i` and/or release using `rez-release`.

### Non-rez installation
Using rez for deployment is recommended, but the following steps can be used to install without rez:
- Clone this repository.
- Configure `NodeManager` using the config (see below).
- Update your environment with the following PATHS referencing `NodeManager` in the location we cloned it to:
  - HOUDINI_MENU_PATH: `<PATH_TO_NODE_MANAGER>/dcc/houdini/menu`.
  - HOUDINI_PATH: `<PATH_TO_NODE_MANAGER>/dcc/houdini`.
  - PYTHONPATH: `<PATH_TO_NODE_MANAGER>/lib/python`.
HOUDINI_MENU_PATH="/Users/jcox/source/github/node_manager/dcc/houdini/menu:&";export HOUDINI_PATH="/Users/jcox/source/github/node_manager/dcc/houdini:&";export PYTHONPATH="/Users/jcox/source/github/node_manager/lib/python:/Users/jcox/source/external/python_lib";export NODE_MANAGER_REPOS="/Users/jcox/hdas

## Configure NodeManager

## Plugin System
Node Manager supports a plugin system which can be used to configure the behaviour at different points of the workflow. The current stages where plugins operate are detailed below.

### Discover Plugins
Discover plugins allow us to customise the way that Node Manager can find the various definition repositories that will be used to load node definitions. It then creates `NodeManager.Repo` objects based on these.

- `DefaultDiscover`: The default discover plugin. This looks for a comma-separated list of repo paths from the `NODE_MANAGER_REPOS` environment variable.

### Edit Plugins
Edit plugins allow customisation of the way that a definition can be placed into an editable state.

- `DefaultEdit`: If the definition can be edited in it's current location leave it there, otherwise move it to the pre-defined edit directory.

### Load Plugins
Load plugins allow us to customise the way that a Node Manager Repo loads it's definitions.

- `DefaultLoad`: Load all node definitions found in the repository path, installing the definitions into the current session and tracking them through `NodeManager`.
- `GitLoad`: Clone the Git Repository and then expand the Node Definitions found there into the temp directory. Install the definitions into the current session and keep track of them with the `NodeManager`.

### Publish Plugins
Publish plugins allow customisation of the way changed node definitions can be published.

- `DefaultPublish`: Disk based publish, where the node definition file is moved back to the repo it was loaded from. After completion the definition being used in the current session switched to use the new version.

- `GitPublish`: The node definition is expanded to disk and then pushed to source control for the repo it was loaded from. After completion the defintion used in the current session is switched to use the newly commited version.
