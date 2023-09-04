#!/usr/bin/env python

"""Node manager utils."""

import logging
import time


logger = logging.getLogger(__name__)


def embedded_definition(definition):
    """
    Determine if the given hou.HDADefinition is embedded.

    Args:
        definition(hou.HDADefinition): The definition to check.

    Returns:
        (bool): Is the definition embedded.
    """
    if definition.libraryFilePath() == "Embedded":
        return True

    return False


def valid_node_type_name(node_type_name):
    """
    Validate the nodeTypeName for the given hou.HDADefinition.

    Args:
        node_type_name(str): The node type name to validate.

    Returns:
        (bool): Is the node type name valid?
    """
    name_components = node_type_name_components(node_type_name)
    if len(name_components) >= 3:
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
        return name_sections[-3]

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


def cleanup_embedded_definitions(nodetype):
    """
    Cleanup any embedded definition found for the given nodetype.

    Args:
        nodetype(hou.NodeType): The nodetype to clean-up any embedded defintions for.
    """
    for definition in nodetype.allInstalledDefinitions():
        if embedded_definition(definition) and not definition.isCurrent():
            definition.destroy()
            logger.debug(
                "Embedded definition removed for {name}.".format(
                    name=nodetype.name(),
                )
            )


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
    return "release_{category}-{namespace}-{name}-{version}-{time}".format(
        category=category,
        namespace=namespace,
        name=name,
        version=version,
        time=release_time,
    )


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
    return "{category}_{namespace}_{name}.hda".format(
        category=category, namespace=namespace, name=name
    )
