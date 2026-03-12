import pytest
from unittest.mock import MagicMock, patch
import os
import shutil
import hou
from node_manager.utils import definitionutils

def test_embedded_definition():
    mock_definition = MagicMock()
    mock_definition.libraryFilePath.return_value = "Embedded"
    assert definitionutils.embedded_definition(mock_definition) is True
    
    mock_definition.libraryFilePath.return_value = "/path/to/hda"
    assert definitionutils.embedded_definition(mock_definition) is False

def test_uninstall_definition():
    mock_definition = MagicMock()
    mock_definition.libraryFilePath.return_value = "/path/to/my.hda"
    
    with patch("hou.hda.uninstallFile") as mock_uninstall:
        with patch("os.makedirs") as mock_makedirs:
            with patch("shutil.move") as mock_move:
                with patch("os.path.exists", return_value=False):
                    definitionutils.uninstall_definition(mock_definition, backup_dir="/backup")
                    mock_uninstall.assert_called_once_with("/path/to/my.hda")
                    mock_makedirs.assert_called_once_with("/backup")
                    mock_move.assert_called_once_with("/path/to/my.hda", "/backup")

                # Test without backup_dir
                mock_uninstall.reset_mock()
                mock_makedirs.reset_mock()
                mock_move.reset_mock()
                with patch("os.path.exists", return_value=True):
                    definitionutils.uninstall_definition(mock_definition)
                    mock_uninstall.assert_called_once_with("/path/to/my.hda")
                    mock_makedirs.assert_not_called()
                    mock_move.assert_called_once_with("/path/to/my.hda", "/path/to/backup")

def test_cleanup_embedded_definitions():
    mock_nodetype = MagicMock()
    mock_def1 = MagicMock()
    mock_def1.libraryFilePath.return_value = "Embedded"
    mock_def1.isCurrent.return_value = False
    
    mock_def2 = MagicMock()
    mock_def2.libraryFilePath.return_value = "/path/to/hda"
    mock_def2.isCurrent.return_value = False
    
    mock_def3 = MagicMock()
    mock_def3.libraryFilePath.return_value = "Embedded"
    mock_def3.isCurrent.return_value = True
    
    mock_nodetype.allInstalledDefinitions.return_value = [mock_def1, mock_def2, mock_def3]
    
    definitionutils.cleanup_embedded_definitions(mock_nodetype)
    mock_def1.destroy.assert_called_once()
    mock_def2.destroy.assert_not_called()
    mock_def3.destroy.assert_not_called()

def test_create_definition_copy():
    mock_definition = MagicMock()
    mock_definition.nodeTypeName.return_value = "test::node::1.0.0"
    
    with patch("node_manager.utils.editable_hda_path_from_components", return_value="/tmp/edit.hda"):
        with patch("node_manager.utils.nodetypeutils.node_type_name_from_components", return_value="new::node::2.0.0"):
            with patch("hou.hda.installFile") as mock_install:
                result = definitionutils.create_definition_copy(mock_definition, "/tmp", namespace="new", version="2.0.0")
                assert result == "new::node::2.0.0"
                mock_definition.copyToHDAFile.assert_called_once_with("/tmp/edit.hda", new_name="new::node::2.0.0")
                mock_install.assert_called_once()

                # Test no name change
                mock_definition.copyToHDAFile.reset_mock()
                result = definitionutils.create_definition_copy(mock_definition, "/tmp")
                assert result is None
                mock_definition.copyToHDAFile.assert_called_once_with("/tmp/edit.hda", new_name=None)
