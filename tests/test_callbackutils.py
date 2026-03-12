import pytest
from unittest.mock import MagicMock, patch
import hou
from node_manager.utils import callbackutils

def test_cosmetic_callbacks_enabled_no_ui():
    with patch("hou.isUIAvailable", return_value=False):
        assert callbackutils.cosmetic_callbacks_enabled() is False

def test_cosmetic_callbacks_enabled_with_ui():
    if not hasattr(hou, "ui"):
        hou.ui = MagicMock()
    with patch("hou.isUIAvailable", return_value=True):
        with patch("hou.ui.paneTabOfType", return_value=MagicMock()):
            assert callbackutils.cosmetic_callbacks_enabled() is True

def test_cosmetic_callbacks_enabled_exception():
    if not hasattr(hou, "ui"):
        hou.ui = MagicMock()
    with patch("hou.isUIAvailable", return_value=True):
        with patch("hou.ui.paneTabOfType", side_effect=hou.NotAvailable):
            assert callbackutils.cosmetic_callbacks_enabled() is False

def test_node_changed_no_manager():
    with patch("node_manager.utils.get_manager", return_value=None):
        # Should return early
        assert callbackutils.node_changed(MagicMock()) is None

def test_node_changed_cosmetic_disabled():
    mock_manager = MagicMock()
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        with patch("node_manager.utils.callbackutils.cosmetic_callbacks_enabled", return_value=False):
            # Should return early
            assert callbackutils.node_changed(MagicMock()) is None

def test_node_changed_not_digital_asset():
    mock_manager = MagicMock()
    mock_node = MagicMock()
    mock_node.path.return_value = "/obj/geo1"
    mock_node.name.return_value = "geo1"
    
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        with patch("node_manager.utils.callbackutils.cosmetic_callbacks_enabled", return_value=True):
            with patch("node_manager.utils.nodeutils.is_digital_asset", return_value=False):
                # Should return early
                assert callbackutils.node_changed(mock_node) is None

def test_node_changed_success():
    mock_manager = MagicMock()
    mock_manager.is_node_manager_node.return_value = True
    mock_node = MagicMock()
    mock_node.path.return_value = "/obj/geo1"
    mock_node.name.return_value = "geo1"
    
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        with patch("node_manager.utils.callbackutils.cosmetic_callbacks_enabled", return_value=True):
            with patch("node_manager.utils.nodeutils.is_digital_asset", return_value=True):
                with patch("node_manager.utils.nodeutils.node_comment") as mock_comment:
                    callbackutils.node_changed(mock_node)
                    mock_comment.assert_called_once_with(mock_node, published=True)
