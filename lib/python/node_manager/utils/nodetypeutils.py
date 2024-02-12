#!/usr/bin/env python

"""Houdini NodeType utils."""

import logging


logger = logging.getLogger(__name__)


def definition_subdir(name, category):
    """Get the definition subdirectory name.

    Args:
        name(str): The node type name.
        category(str): The node type category.

    Returns:
        (str): The definition subdirectory name.
    """
    return "{namespace}_8_8{category}_1{typename}_8_8{version}".format(
        namespace=node_type_namespace(name),
        category=category,
        typename=node_type_name(name),
        version=node_type_version(name),
    )


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
