#!/usr/bin/env python

"""Node manager utils."""

import logging
import os
import time

from node_manager import manager


logger = logging.getLogger(__name__)


def get_manager():
    """Get the node manager instance if one exists.

    Returns:
        node_manager.NodeManager: The current instance of Node Manager.
    """
    manager_instance = manager.NodeManager.instance
    if not manager_instance:
        raise RuntimeError("Node Manager not initialised.")
    return manager_instance


def using_rez():
    """Check if the current session is using Rez.

    Returns:
        (bool): Is the current session using Rez?
    """
    return os.environ.get("REZ_NODE_MANAGER_BASE") is not None


def valid_node_type_name(node_type_name):
    """
    Validate the nodeTypeName for the given hou.HDADefinition.

    Args:
        node_type_name(str): The node type name to validate.

    Returns:
        (bool): Is the node type name valid?
    """
    name_components = node_type_name_components(node_type_name)
    if len(name_components) >= 2:
        return True

    return False


def node_type_name_components(node_type_name):
    """Get the node type components.

    A hou.HDADefinition nodeTypeName is formated as follows: namespace::name::version.
    For a given node type name return a list of the various components.

    Args:
        node_type_name(str): The node type name toy get the components from.

    Returns:
        (list): A list of name components.
    """
    return node_type_name.split("::")


def node_type_namespace(node_type_name, new_namespace=None):
    """Get the node type namespace.

    Get the nodeType namespace from the given nodeTypeName, or use te new namespace if
    one has been provided.

    Args:
        node_type_name(str): The node type name to get the namespace from.
        new_namespace(:obj:`str`,optional): The updated namespace.

    Returns:
        (str): The namespace extracted from the node type name.
    """
    if new_namespace:
        return new_namespace

    if valid_node_type_name(node_type_name):
        name_sections = node_type_name_components(node_type_name)
        namespace_name_sections = name_sections[:-2]
        return ".".join(namespace_name_sections)

    return None


def node_type_name(node_type_name, new_name=None):
    """Get the node type name.

    Get the nodeType name from the given nodeTypeName, or use te new name if one has
    been provided.

    Args:
        node_type_name(str): The node type name to get the name from.
        new_name(:obj:`str`,optional): The updated name.

    Returns:
        (str): The name extracted from the node type name.
    """
    if new_name:
        return new_name

    if valid_node_type_name(node_type_name):
        name_sections = node_type_name_components(node_type_name)
        return name_sections[-2]

    return node_type_name


def node_type_version(node_type_name, new_version=None):
    """Get the node type version.

    Get the nodeType version from the given nodeTypeName, or use te new version if one
    has been provided.

    Args:
        node_type_name(str): The node type name to get the version from.
        new_version(:obj:`str`,optional): The updated version number.

    Returns:
        (str): The version extracted from the node type name.
    """
    if new_version:
        return new_version

    if valid_node_type_name(node_type_name):
        name_sections = node_type_name_components(node_type_name)
        return name_sections[-1]

    return None


def node_type_index(node_type_name, category):
    """Generate a node type index.

    We use namespace::category/name as our index for our NodeTypes stored in the
    manager. Use the given hou.HDADefinition to generate an index.

    Args:
        node_type_name(str): The full node type name to lookup against.
        category(str): The node type category to lookup against.

    Returns:
        index(str): The node type index based on the given criteria.
    """
    index = None
    if valid_node_type_name(node_type_name):
        name_sections = node_type_name_components(node_type_name)
        name_sections[-2] = "{category}/{name}".format(
            category=category, name=name_sections[-2]
        )
        index = "::".join(name_sections[:-1])

    return index


def release_branch_name(definition):
    """
    Generate a legal git release branch name for the given definition.

    Args:
        definition(hou.HDADefinition): The HDA definition to get the release branch for.

    Returns:
        (str): The git release branch for the given definition.
    """
    category = definition.nodeTypeCategory().name()
    current_name = definition.nodeTypeName()
    namespace = node_type_namespace(current_name)
    name = node_type_name(current_name)
    version = node_type_version(current_name)
    ts = time.gmtime()
    release_time = time.strftime("%d-%m-%y-%H-%M-%S", ts)
    return "release_{category}-{namespace}{name}-{version}-{time}".format(
        category=category,
        namespace="{namespace}-".format(namespace=namespace) if namespace else "",
        name=name,
        version=version,
        time=release_time,
    )


def node_type_name_from_components(definition, namespace=None, name=None, version=None):
    """Generate a node type name based on its components.

    Generate a new nodeTypeName for the given hou.HDADefinition updating the namespace,
    name and version if provided.

    Args:
        definition(hou.HDADefinition): The HDA definition to generate the node type name
            for.
        namespace(:obj:`str`,optional): The new namespace to use for the definition.
        name(:obj:`str`,optional): The new name to use for the definition.
        version(:obj:`str`,optional): The new version to use for the definition.

    Returns:
        (str): The updated node type name.
    """
    current_name = definition.nodeTypeName()
    new_namespace = node_type_namespace(current_name, new_namespace=namespace)
    new_name = node_type_name(current_name, new_name=name)
    new_version = node_type_version(current_name, new_version=version)
    return "{namespace}::{name}::{version}".format(
        namespace=new_namespace, name=new_name, version=new_version
    )


def editable_hda_path_from_components(definition, edit_dir, namespace=None, name=None):
    """Get the editable HDA path.

    Generate a file path where a hou.HDADefinition can be edited within the given edit
    directory. If a new nodeType namespace or name has been provided take it into
    account when generating the path.

    Args:
        definition(hou.HDADefinition): The HDA definition to generate the editable HDA
            path for.
        edit_dir(str): The root edit directory.
        namespace(str): The updated namespace to use if it is being changed.
        name(str): The updated name to use if it is being changed.

    Returns:
        (str): The editable HDA path on disk.
    """
    category = definition.nodeTypeCategory()
    current_name = definition.nodeTypeName()
    if valid_node_type_name(current_name):
        # If the name is valid, use it
        logger.debug("Using valid node type name: %s", current_name)
        new_namespace = node_type_namespace(current_name, new_namespace=namespace)
        new_name = node_type_name(current_name, new_name=name)
        full_name = "{namespace}_{name}".format(namespace=new_namespace, name=new_name)
    else:
        # Otherwise just make do with whatever we have
        logger.debug("Using invalid node type name: %s", current_name)
        full_name = definition.nodeType().nameComponents()[2]

    editable_name = "{category}_{full_name}.{time}.hda".format(
        category=category.name(), full_name=full_name, time=int(time.time())
    )

    logger.debug("Editable name: %s", editable_name)
    logger.debug("Edit dir: %s", edit_dir)

    return os.path.join(edit_dir, editable_name)


def expanded_hda_name(definition):
    """Get the expanded HDA name.

    This function is used by the HDA manager to set the name of the directory a
    hou.HDADefinition is expanded to
    hou.nodeTypeCategory.name()_hou.nodeTypeName(namespace)_hou.nodeTypeName(name).hda
    ie. Lop_rebellion.pipeline_sgreference.hda.

    Args:
        definition(hou.HDADefinition): The HDA definition to get the expanded name for.

    Returns:
        (str): The expanded HDA name.
    """
    category = definition.nodeTypeCategory().name()
    current_name = definition.nodeTypeName()
    name = node_type_name(current_name)
    namespace = node_type_namespace(current_name)
    version = node_type_version(current_name)
    return "{category}_{namespace}{name}.{version}.hda".format(
        category=category,
        namespace="{namespace}.".format(namespace=namespace) if namespace else "",
        name=name,
        version=version,
    )
