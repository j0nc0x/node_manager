import os
import pytest
import hou
from node_manager.utils import nodetypeutils

def test_node_type_name_components():
    assert nodetypeutils.node_type_name_components("test::node::1.0.0") == ["test", "node", "1.0.0"]
    assert nodetypeutils.node_type_name_components("node::1.0.0") == ["node", "1.0.0"]
    assert nodetypeutils.node_type_name_components("node") == ["node"]
    assert nodetypeutils.node_type_name_components("") == [""]

def test_valid_node_type_name():
    assert nodetypeutils.valid_node_type_name("test::node::1.0.0") is True
    assert nodetypeutils.valid_node_type_name("node::1.0.0") is True
    assert nodetypeutils.valid_node_type_name("node") is False
    assert nodetypeutils.valid_node_type_name("") is False

def test_node_type_namespace():
    assert nodetypeutils.node_type_namespace("test::node::1.0.0") == "test"
    assert nodetypeutils.node_type_namespace("org.test::node::1.0.0") == "org.test"
    assert nodetypeutils.node_type_namespace("a::b::c::1.0.0") == "a.b"
    assert nodetypeutils.node_type_namespace("node::1.0.0") == ""
    assert nodetypeutils.node_type_namespace("node") is None
    assert nodetypeutils.node_type_namespace("test::node::1.0.0", new_namespace="new") == "new"

def test_node_type_name():
    assert nodetypeutils.node_type_name("test::node::1.0.0") == "node"
    assert nodetypeutils.node_type_name("node::1.0.0") == "node"
    assert nodetypeutils.node_type_name("node") == "node"
    assert nodetypeutils.node_type_name("test::node::1.0.0", new_name="new_node") == "new_node"

def test_node_type_version():
    assert nodetypeutils.node_type_version("test::node::1.0.0") == "1.0.0"
    assert nodetypeutils.node_type_version("node::1.0.0") == "1.0.0"
    assert nodetypeutils.node_type_version("node") is None
    assert nodetypeutils.node_type_version("test::node::1.0.0", new_version="2.0.0") == "2.0.0"

def test_node_type_name_from_components():
    hda_path = os.path.join(os.path.dirname(__file__), "hda", "test_test_sop_node_1_0_0.hda")
    definitions = hou.hda.definitionsInFile(hda_path)
    definition = definitions[0]

    current_name = definition.nodeTypeName()

    # No changes
    assert nodetypeutils.node_type_name_from_components(definition) == current_name

    # Change namespace
    expected_ns = "new_ns::test_sop_node::1.0.0"
    assert nodetypeutils.node_type_name_from_components(definition, namespace="new_ns") == expected_ns

    # Change name
    expected_name = "test::new_node::1.0.0"
    assert nodetypeutils.node_type_name_from_components(definition, name="new_node") == expected_name

    # Change version
    expected_version = "test::test_sop_node::2.0.0"
    assert nodetypeutils.node_type_name_from_components(definition, version="2.0.0") == expected_version

    # Change all
    assert nodetypeutils.node_type_name_from_components(definition, namespace="a", name="b", version="c") == "a::b::c"
