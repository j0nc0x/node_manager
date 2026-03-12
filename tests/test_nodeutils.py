import pytest
from unittest.mock import MagicMock, patch
import os
import hou
from node_manager.utils import nodeutils

def test_node_comment():
    mock_node = MagicMock()
    mock_node.isInsideLockedHDA.return_value = False
    
    nodeutils.node_comment(mock_node, published=True)
    mock_node.setComment.assert_called_with("Node Manager: Published")
    
    nodeutils.node_comment(mock_node, published=False)
    mock_node.setComment.assert_called_with("Node Manager: Editable")

    # Test locked node
    mock_node.reset_mock()
    mock_node.isInsideLockedHDA.return_value = True
    nodeutils.node_comment(mock_node)
    mock_node.setComment.assert_not_called()

def test_node_at_path():
    with patch("hou.node", return_value=MagicMock()) as mock_node_func:
        nodeutils.node_at_path("/obj/geo1")
        mock_node_func.assert_called_once_with("/obj/geo1")

    # Test no node found
    with patch("hou.node", return_value=None):
        assert nodeutils.node_at_path("/non/existent") is None

def test_type_name():
    mock_node = MagicMock()
    mock_node.type().nameComponents.return_value = ["a", "b", "c"]
    mock_node.type().name.return_value = "a::b::c"
    
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_node):
        assert nodeutils.type_name("/obj/geo1", short=True) == "c"
        assert nodeutils.type_name("/obj/geo1", short=False) == "a::b::c"

    # Test no node found
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=None):
        assert nodeutils.type_name("/non/existent") is None

def test_has_node_type():
    mock_node = MagicMock()
    mock_node.type().category().name.return_value = "Sop"
    
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_node):
        with patch("node_manager.utils.nodeutils.type_name", return_value="my_type"):
            assert nodeutils.has_node_type("/obj/geo1", "my_type", category="Sop") is True
            assert nodeutils.has_node_type("/obj/geo1", "other_type", category="Sop") is False
            assert nodeutils.has_node_type("/obj/geo1", "my_type", category="Obj") is False

    # Test no node found with category
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=None):
        assert nodeutils.has_node_type("/non/existent", "my_type", category="Sop") is False

def test_all_nodes_of_type():
    mock_node1 = MagicMock()
    mock_node1.path.return_value = "/obj/geo1"
    mock_node2 = MagicMock()
    mock_node2.path.return_value = "/obj/geo2"
    
    with patch("hou.root") as mock_root:
        mock_root_node = MagicMock()
        mock_root.return_value = mock_root_node
        mock_root_node.recursiveGlob.return_value = [mock_node1, mock_node2]
        with patch("node_manager.utils.nodeutils.type_name", side_effect=["type1", "type2"]):
            nodes = nodeutils.all_nodes_of_type("type1")
            assert len(nodes) == 1
            assert nodes[0] == mock_node1

    # Test no nodes found
    with patch("hou.root") as mock_root:
        mock_root_node = MagicMock()
        mock_root.return_value = mock_root_node
        mock_root_node.recursiveGlob.return_value = []
        assert nodeutils.all_nodes_of_type("type1") == []

def test_get_user_data():
    mock_node = MagicMock()
    mock_node.isInsideLockedHDA.return_value = False
    mock_node.userData.return_value = "value"
    
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_node):
        assert nodeutils.get_user_data("/obj/geo1", "key") == "value"

    # Test locked node with unlocked parent
    mock_locked_node = MagicMock()
    mock_locked_node.isInsideLockedHDA.return_value = True
    mock_locked_node.path.return_value = "/obj/geo1/locked"
    mock_parent_node = MagicMock()
    mock_parent_node.isInsideLockedHDA.return_value = False
    mock_parent_node.path.return_value = "/obj/geo1"
    mock_parent_node.userData.return_value = "parent_value"
    mock_locked_node.parent.return_value = mock_parent_node

    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_locked_node):
        assert nodeutils.get_user_data("/obj/geo1/locked", "key") == "parent_value"
        mock_parent_node.userData.assert_called_with("/obj/geo1/locked.key")

    # Test locked node with no unlocked parent
    mock_parent_node.isInsideLockedHDA.return_value = True
    mock_parent_node.parent.return_value = None
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_locked_node):
        with pytest.raises(RuntimeError):
            nodeutils.get_user_data("/obj/geo1/locked", "key")

    # Test no node found
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=None):
        assert nodeutils.get_user_data("/non/existent", "key") is None

def test_set_user_data():
    mock_node = MagicMock()
    mock_node.isInsideLockedHDA.return_value = False
    
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_node):
        nodeutils.set_user_data("/obj/geo1", "key", "value")
        mock_node.setUserData.assert_called_with("key", "value")

    # Test locked node with unlocked parent
    mock_locked_node = MagicMock()
    mock_locked_node.isInsideLockedHDA.return_value = True
    mock_locked_node.path.return_value = "/obj/geo1/locked"
    mock_parent_node = MagicMock()
    mock_parent_node.isInsideLockedHDA.return_value = False
    mock_parent_node.path.return_value = "/obj/geo1"
    mock_locked_node.parent.return_value = mock_parent_node

    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_locked_node):
        nodeutils.set_user_data("/obj/geo1/locked", "key", "value")
        mock_parent_node.setUserData.assert_called_with("/obj/geo1/locked.key", "value")

    # Test locked node with no unlocked parent
    mock_parent_node.isInsideLockedHDA.return_value = True
    mock_parent_node.parent.return_value = None
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_locked_node):
        with pytest.raises(RuntimeError):
            nodeutils.set_user_data("/obj/geo1/locked", "key", "value")

def test_definition_from_node():
    mock_node = MagicMock()
    mock_node.type().definition.return_value = MagicMock()
    
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=mock_node):
        assert nodeutils.definition_from_node("/obj/geo1") is not None

    # Test no node found
    with patch("node_manager.utils.nodeutils.node_at_path", return_value=None):
        assert nodeutils.definition_from_node("/non/existent") is None

def test_is_digital_asset():
    mock_definition = MagicMock()
    mock_definition.libraryFilePath.return_value = "/path/to/hda"
    
    with patch("node_manager.utils.nodeutils.definition_from_node", return_value=mock_definition):
        with patch.dict("node_manager.config.node_manager_config", {"hda_exclude_path": ["/exclude"]}):
            with patch("os.getenv", side_effect=lambda k: "/hfs" if k == "HFS" else None):
                assert nodeutils.is_digital_asset("/obj/geo1") is True
                
                mock_definition.libraryFilePath.return_value = "/exclude/my.hda"
                assert nodeutils.is_digital_asset("/obj/geo1") is False

                # Test include_hidden
                assert nodeutils.is_digital_asset("/obj/geo1", include_hidden=True) is True

                # Test NODE_MANAGER_HDA_EXCLUDE_PATH
                mock_definition.libraryFilePath.return_value = "/env_exclude/my.hda"
                with patch("os.getenv", side_effect=lambda k: "/env_exclude" if k == "NODE_MANAGER_HDA_EXCLUDE_PATH" else ("/hfs" if k == "HFS" else None)):
                    assert nodeutils.is_digital_asset("/obj/geo1") is False

                # Test HFS exclude
                mock_definition.libraryFilePath.return_value = "/hfs/my.hda"
                with patch("os.getenv", side_effect=lambda k: "/hfs" if k == "HFS" else None):
                    assert nodeutils.is_digital_asset("/obj/geo1") is False

                # Test HFS not set
                with patch("os.getenv", return_value=None):
                    mock_definition.libraryFilePath.return_value = "/some/path"
                    assert nodeutils.is_digital_asset("/obj/geo1") is True

    # Test no definition
    with patch("node_manager.utils.nodeutils.definition_from_node", return_value=None):
        assert nodeutils.is_digital_asset("/obj/geo1") is False

def test_force_ui_update():
    mock_parm = MagicMock()
    with patch("hou.parm", return_value=mock_parm):
        nodeutils.force_ui_update(["/obj/geo1/parm"])
        mock_parm.pressButton.assert_called_once()

    # Test parm not found
    with patch("hou.parm", return_value=None):
        nodeutils.force_ui_update(["/non/existent/parm"])
