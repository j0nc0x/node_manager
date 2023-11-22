#!/usr/bin/env python

"""Houdini NodeType utils."""

import logging


logger = logging.getLogger(__name__)


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