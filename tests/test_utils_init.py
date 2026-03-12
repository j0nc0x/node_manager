import pytest
from unittest.mock import MagicMock, patch
import os
import hou
import time
from node_manager import utils

def test_get_manager():
    with patch("node_manager.manager.NodeManager.instance", new=MagicMock()) as mock_instance:
        assert utils.get_manager() == mock_instance
    
    with patch("node_manager.manager.NodeManager.instance", new=None):
        assert utils.get_manager() is None

def test_display_message_no_ui():
    with patch("hou.isUIAvailable", return_value=False):
        assert utils.display_message("test message") is None
        
        # Test different severities for logging coverage
        utils.display_message("error message", severity=hou.severityType.Error)
        utils.display_message("warning message", severity=hou.severityType.Warning)
        utils.display_message("fatal message", severity=hou.severityType.Fatal)

def test_display_message_with_ui():
    if not hasattr(hou, "ui"):
        hou.ui = MagicMock()
    with patch("hou.isUIAvailable", return_value=True):
        with patch("hou.ui.displayMessage", return_value=0) as mock_display:
            assert utils.display_message("test message") == 0
            mock_display.assert_called_once()

def test_node_type_index():
    assert utils.node_type_index("test::node::1.0.0", "Sop") == "test::Sop/node"
    assert utils.node_type_index("node", "Sop") is None

def test_release_branch_name():
    mock_definition = MagicMock()
    mock_definition.nodeTypeCategory().name.return_value = "Sop"
    mock_definition.nodeTypeName.return_value = "test::node::1.0.0"
    
    with patch("time.strftime", return_value="01-01-26-12-00-00"):
        branch = utils.release_branch_name(mock_definition)
        assert "release_Sop-test-node-1.0.0-01-01-26-12-00-00" == branch

        # Test no namespace
        mock_definition.nodeTypeName.return_value = "node::1.0.0"
        branch = utils.release_branch_name(mock_definition)
        assert "release_Sop-node-1.0.0-01-01-26-12-00-00" == branch

def test_editable_hda_path_from_components():
    mock_definition = MagicMock()
    mock_definition.nodeTypeCategory().name.return_value = "Sop"
    mock_definition.nodeTypeName.return_value = "test::node::1.0.0"
    
    with patch("time.time", return_value=123456789):
        path = utils.editable_hda_path_from_components(mock_definition, "/tmp")
        assert path == "/tmp/Sop_test_node.123456789.hda"

        # Test overrides
        path = utils.editable_hda_path_from_components(mock_definition, "/tmp", namespace="new", name="other")
        assert path == "/tmp/Sop_new_other.123456789.hda"

        # Test invalid node type name
        mock_definition.nodeTypeName.return_value = "invalid_name"
        mock_definition.nodeType().nameComponents.return_value = ["", "", "fallback"]
        path = utils.editable_hda_path_from_components(mock_definition, "/tmp")
        assert path == "/tmp/Sop_fallback.123456789.hda"

def test_expanded_hda_name():
    mock_definition = MagicMock()
    mock_definition.nodeTypeCategory().name.return_value = "Sop"
    mock_definition.nodeTypeName.return_value = "test::node::1.0.0"
    
    assert utils.expanded_hda_name(mock_definition) == "Sop_test.node.1.0.0.hda"

    # Test no namespace
    mock_definition.nodeTypeName.return_value = "node::1.0.0"
    assert utils.expanded_hda_name(mock_definition) == "Sop_node.1.0.0.hda"

def test_is_released():
    with patch.dict("node_manager.config.node_manager_config", {"released_locations": ["/released"]}):
        assert utils.is_released("/released/my.hda") is True
        assert utils.is_released("/work/my.hda") is False

def test_expand_namespaces():
    with patch("getpass.getuser", return_value="jon"):
        assert utils.expand_namespaces(["dev.{user}", "prod"]) == ["dev.jon", "prod"]
