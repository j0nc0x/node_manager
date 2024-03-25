# Node Manager Release Notes

## 0.3.0 (xx/xx/24)
### Features
#### Add Pyblish Support (https://github.com/j0nc0x/node_manager/issues/18)
- Added validate plugins to handle validation workflow.
- `DefaultValidate` includes some very basic non-GUI based validation.
- `PyblishValidate` implements a Pyblish validation process along with a default set of validation plugins.
### Bugfixes
#### Tidy up logging messages for nodes with different namespaces (https://github.com/j0nc0x/node_manager/issues/16)
- Updating logger messages to be a bit more tidy.
#### Simplify Pyblish setup (https://github.com/j0nc0x/node_manager/issues/24)
- Simplify Pyblish setup by using Pyblish Lite instead of PyblishQML.
#### Include pyblish rez package and missing requirements (https://github.com/j0nc0x/node_manager/issues/27)
- Include missing package dependency.
- Include missing requirement docs.
#### Editable definition not cleaned up on release (https://github.com/j0nc0x/node_manager/issues/19)
- If not backup directory is configured use definition-dir/backup.
#### Decrease verbosity of Exclude paths log (https://github.com/j0nc0x/node_manager/issues/29)
- Make log less verbose.
#### Git / Rez Release Issues (https://github.com/j0nc0x/node_manager/issues/13)
- Use temp when cloning to avoid problems from previous release issues.

## 0.2.1 (02/02/24)
### Bugfixes
#### Logger message typo (https://github.com/j0nc0x/node_manager/issues/14)
- Correcting small typo in logger message.

## 0.2.0 (29/01/24)
### Features
#### Ignore SESI HDAs (https://github.com/j0nc0x/node_manager/issues/3)
- Ignore HDAs that reside inside the Houdini installation directory.
- Allow HDAs in other locations to be overriden by using either a config setting (`hda_exclude_path`) or an environment variable (`$NODE_MANAGER_HDA_EXCLUDE_PATH`).
- Allow all HDAs to be considered, including those excluded by the previous point by setting a config option (include_all_hdas).
### Bugfixes
#### Decrease logging verbosity - No NodeType found (https://github.com/j0nc0x/node_manager/issues/5)
- Switch `No NodeType found`. warning to debug to make it less annoying.
- Add more detail to `No NodeType found`. log message to make it more useful for debugging.
- General tidy up.
#### Discard Definition: Internal changes not reverted (https://github.com/j0nc0x/node_manager/issues/7)
- Make sure we match the current node to it's definition during the "Discard Definition" process in order that we also discard any unsaved changes.
#### Node Comment errors for locked HDAs (https://github.com/j0nc0x/node_manager/issues/9)
- Quick fix to stop an error relating to setting of node comments on nodes that live inside of a locked HDA.

## 0.1.0 (23/11/23)
- First release of NodeManager.
