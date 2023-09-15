# Node Manager
Manage and track Houdini HDAs and Nuke Gizmos/Snippets

### General Design Points
- Should feel like the user is just referencing node definitions from a directory on disk. Minimise extra steps.
- All node changes tracked through source control.
- Use standard UIs and workflows where possible.


### Storing / loading the HDAs

#### Versioned Directories
Pros:

- HDAs stored on disk as binary for fast loading.
- More storage due to duplication of data between versions.
- Easily implement solutions to hide / show HDAs being edited and also to chose to see other users WIP.

Cons:

- Less like working with a directory of HDAs on disk.
- HDAs require (auto) copying to a working directory to edit.
- Updates into a live Houdini session cumbersome.


#### Local HDA dir / repo clone:
Pros:

- HDAs pulled and built when required, small disk space wastage.
- Updates into a live Houdini session relatively easy, pull / build the latest refresh HDAs.

Cons:

HDAs pulled and built when required, this will add to load times
  - How to handle merge if heads have diverged on pull.


#### Central HDA dir / local repo clone:
Pros:

- Much more like working with a simple HDA folder on disk.
- You will see all users HDAs as they are being developed.

Cons:

- Technically you will be able to publish anyone's updates (maybe a pro?).
- Difficult to lock changes for use on the farm. Maybe require publish and build from repo on farm.

#### Central HDA dir / auto publish:
Pros:

- Basically a shared folder on disk.
- Publishes happen automatically on certain events - save, submission to farm etc.

Cons:

- Difficult / not possible to capture release comments.
- No choices on when to publish, always include everything (maybe a pro).
- Lock on farm by pulling a certain commit / tag.

### Plugin system
Build plugin system for handling default HDA storage options split into plugin category for load and publish. Allow plugins to be selected using config file.

Load:

- (Default) Basic load from folder on disk.
- Load directly from git with support to load specific commit.
- Load from versioned directory with support for loading specific directory.
- Load from rez package determined from rez environment.

Publish:
- (Default) Basic write to folder on disk.
- Write directly to git applying version tag.
- Write to git and release to versioned directory.
- Write to git and release to rez package.