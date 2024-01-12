# Design Considerations
## Storing / loading the HDAs
### Versioned Directories
Pros:

- HDAs stored on disk as binary for fast loading.
- More storage due to duplication of data between versions.
- Easily implement solutions to hide / show HDAs being edited and also to chose to see other users WIP.

Cons:

- Less like working with a directory of HDAs on disk.
- HDAs require (auto) copying to a working directory to edit.
- Updates into a live Houdini session cumbersome.


### Local HDA dir / repo clone:
Pros:

- HDAs pulled and built when required, small disk space wastage.
- Updates into a live Houdini session relatively easy, pull / build the latest refresh HDAs.

Cons:

HDAs pulled and built when required, this will add to load times
  - How to handle merge if heads have diverged on pull.


### Central HDA dir / local repo clone:
Pros:

- Much more like working with a simple HDA folder on disk.
- You will see all users HDAs as they are being developed.

Cons:

- Technically you will be able to publish anyone's updates (maybe a pro?).
- Difficult to lock changes for use on the farm. Maybe require publish and build from repo on farm.

### Central HDA dir / auto publish:
Pros:

- Basically a shared folder on disk.
- Publishes happen automatically on certain events - save, submission to farm etc.

Cons:

- Difficult / not possible to capture release comments.
- No choices on when to publish, always include everything (maybe a pro).
- Lock on farm by pulling a certain commit / tag.

## Edit Directory

In most cases we can assume the read directory is is write protected, but irrespective of this it would be best to avoid editing the released nodes directly.

Instead we should look to allow the node definition file to be copied to a separate edit directory where it lives during the edit process. Ideally the edit directory should be on a network location and available on any render farm machines if applicable.

We should split the edit directory by username to allow people to edit their node changes separately without treading on each others edits.

The node manager will need to provide a mechanism for placing a copy of the node for editing purposes in the user's edit directory. It should also provide a way of discarding and nodes currently in an edit state.
- Provide UI menu options to allow node to be copied for editing, allowing the major or minor version to be incremented at the same point.
  - Edit - copy to edit directory, no change to version.
  - Edit Major - copy to edit directory, increment major version.
  - Edit Minor - copy to edit directory, increment minor version.
  - Edit Custom - provide the same functionality as in the "Digital Assets - Save As" UI element.


Ideally it would be desirable to feedback to the user whether nodes are in an editable state in the UI. Possibly this could be done with:
- Node message.
- Node colour.

## Plugin system
Implement a plugin system for handling default HDA storage options split into plugin category for load and publish. Allow plugins to be selected using config file.

### (Default) Folder on disk

Load: Basic load from folder on disk.

Publish: Basic write to folder on disk.

### Git

Load: Directly from git with support to load a specific commit.

Publish: Write directly to git applying version tag.

### Git Versioned Directory

Load: From versioned directory with support for loading specific directory.

Publish: Write to git and release to versioned directory.

### Rez Package

Load: From rez package determined from rez environment.

Publish: Write to git and release to rez package.
