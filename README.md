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
  - `HOUDINI_MENU_PATH`: `<NODE_MANAGER_ROOT>/dcc/houdini/menu`.
  - `HOUDINI_PATH`: `<NODE_MANAGER_ROOT>/dcc/houdini`.
  - `PYTHONPATH`: `<NODE_MANAGER_ROOT>/lib/python`.
  
  It is likely you will want to append these paths if they alredy exist.

## Configure NodeManager
### Config File
Currently the method for configuring NodeManager is to edit the config file that is located at `<NODE_MANAGER>/lib/python/config.py`. This is currently a very low-tech solution, but allows the `node_manager_config` dictionary to be set which can be used to reflect various aspects of `NodeManager`.

Config options currently supported:
- `background (bool)`: Should the HDAs be loaded in the background thread.
- `discover_plugin (str)`: The name of the discover plugin to use. If unset use `DefaultDiscover`.
- `load_plugin (str)`: The name of the load plugin to use. If unset use `DefaultLoad`.
- `release_plugin (str)`: The name of the release plugin to use. If unset us `DefaultRelease`.
- `rez_packages_root (str)`: The main path to where rez packages are released.
- `rez_package_name (str)`: The name of the rez package used by `NodeManager`.
- `hda_exclude_path (list(str))`: A list of paths which will be ignored by `NodeManager` when identifying definitions it can work with. Note: this can also be set using the `$NODE_MANAGER_HDA_EXCLUDE_PATH` environment variable.
- `include_all_hdas (bool)`: Should the NodeManager consider all HDAs, including those excluded because they are part of the SESI installation or are excluded via either of the previous methods.

### Environment Variables
Some elements of the NodeManager can be configured by setting environment variables.

Currently supported variables are:
- `$NODE_MANAGER_HDA_EXCLUDE_PATH`: A `os.pathsep` separated list of paths which will be ignored by `NodeManager` when identifying definitions it can work with. Note: this can also be set using the `$NODE_MANAGER_HDA_EXCLUDE_PATH` environment variable.

### Plugin System
Node Manager supports a plugin system which can be used to configure the behaviour at different points of the workflow. The current stages where plugins operate are detailed below.

#### Discover Plugins
Discover plugins allow us to customise the way that Node Manager can find the various definition repositories that will be used to load node definitions. It then creates `NodeManager.Repo` objects based on these.

- `DefaultDiscover`: The default discover plugin. This looks for a comma-separated list of repo paths from the `NODE_MANAGER_REPOS` environment variable.

#### Edit Plugins
Edit plugins allow customisation of the way that a definition can be placed into an editable state.

- `DefaultEdit`: If the definition can be edited in it's current location leave it there, otherwise move it to the pre-defined edit directory.

#### Load Plugins
Load plugins allow us to customise the way that a Node Manager Repo loads it's definitions.

- `DefaultLoad`: Load all node definitions found in the repository path, installing the definitions into the current session and tracking them through `NodeManager`.
- `GitLoad`: Clone the Git Repository and then expand the Node Definitions found there into the temp directory. Install the definitions into the current session and keep track of them with the `NodeManager`.
- `RezLoad`: Load all node definitions found in the repository path (which should be a rez package). 

#### Release Plugins
Release plugins allow customisation of the way changed node definitions can be published.

- `DefaultRelease`: Disk based release, where the node definition file is moved back to the repo it was loaded from. After completion the definition being used in the current session is switched to use the new version.
- `GitRelease`: The node definition is expanded to disk and then pushed to source control for the repo it was loaded from. After completion the defintion used in the current session is switched to use the newly commited version.
- `RezRelease`: The node definition is expanded and pushed to source control as with `GitRelease`. Following this the associated rez package is released, and the newly released HDA from there is updated in the current session.
