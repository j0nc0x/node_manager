import pytest
from unittest.mock import MagicMock, patch
import os
from node_manager.utils import pluginutils

def test_path_import():
    with patch("importlib.util.spec_from_file_location") as mock_spec_from_file:
        with patch("importlib.util.module_from_spec") as mock_module_from_spec:
            mock_spec = MagicMock()
            mock_spec_from_file.return_value = mock_spec
            mock_module = MagicMock()
            mock_module_from_spec.return_value = mock_module
            
            result = pluginutils.path_import("/path/to/plugin.py")
            assert result == mock_module
            mock_spec.loader.exec_module.assert_called_once_with(mock_module)

def test_initialise_plugin():
    mock_module = MagicMock()
    mock_plugin = MagicMock()
    mock_plugin.name = "TestPlugin"
    mock_plugin.plugin_type = "TestType"
    mock_module.NodeManagerPlugin.return_value = mock_plugin
    
    result = pluginutils.initialise_plugin(mock_module, arg1="value")
    assert result == mock_plugin
    mock_module.NodeManagerPlugin.assert_called_once_with(arg1="value")

def test_import_plugins_from_path():
    with patch("os.listdir", return_value=["plugin1.py", "__init__.py", ".ignore.py", "not_a_plugin.txt"]):
        with patch("node_manager.utils.pluginutils.path_import", return_value=MagicMock()) as mock_import:
            plugins = pluginutils.import_plugins_from_path("/path/to/plugins")
            assert len(plugins) == 1
            mock_import.assert_called_once_with("/path/to/plugins/plugin1.py")

def test_import_plugins():
    with patch("node_manager.utils.pluginutils.import_plugins_from_path", return_value=[MagicMock()]) as mock_import_path:
        with patch.dict("os.environ", {"NODE_MANAGER_PLUGINS_PATH": "/extra/plugins"}):
            with patch("os.path.isdir", return_value=True):
                plugins = pluginutils.import_plugins()
                assert len(plugins) == 2
                assert mock_import_path.call_count == 2

        # Test empty NODE_MANAGER_PLUGINS_PATH
        mock_import_path.reset_mock()
        with patch.dict("os.environ", {"NODE_MANAGER_PLUGINS_PATH": ""}):
             plugins = pluginutils.import_plugins()
             assert len(plugins) == 1
             mock_import_path.assert_called_once()

def test_get_discover_plugin():
    mock_manager = MagicMock()
    mock_plugin_module = MagicMock()
    mock_plugin_module.NodeManagerPlugin.name = "MyDiscover"
    mock_manager._plugins = [mock_plugin_module]
    
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        # Specific plugin
        result = pluginutils.get_discover_plugin("MyDiscover")
        assert result is not None
        
        # Default plugin
        mock_plugin_module.NodeManagerPlugin.name = "DefaultDiscover"
        result = pluginutils.get_discover_plugin(None)
        assert result is not None

        # Plugin not found
        result = pluginutils.get_discover_plugin("NonExistent")
        assert result is None

def test_get_load_plugin():
    mock_manager = MagicMock()
    mock_plugin_module = MagicMock()
    mock_plugin_module.NodeManagerPlugin.name = "MyLoad"
    mock_manager._plugins = [mock_plugin_module]
    
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        # Specific plugin
        result = pluginutils.get_load_plugin("MyLoad")
        assert result is not None
        
        # Default plugin
        mock_plugin_module.NodeManagerPlugin.name = "DefaultLoad"
        result = pluginutils.get_load_plugin(None)
        assert result is not None

def test_get_edit_plugin():
    mock_manager = MagicMock()
    mock_plugin_module = MagicMock()
    mock_plugin_module.NodeManagerPlugin.name = "MyEdit"
    mock_manager._plugins = [mock_plugin_module]
    
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        # Specific plugin
        result = pluginutils.get_edit_plugin("MyEdit")
        assert result is not None
        
        # Default plugin
        mock_plugin_module.NodeManagerPlugin.name = "DefaultEdit"
        result = pluginutils.get_edit_plugin(None)
        assert result is not None

def test_get_validate_plugin():
    mock_manager = MagicMock()
    mock_plugin_module = MagicMock()
    mock_plugin_module.NodeManagerPlugin.name = "MyValidate"
    mock_manager._plugins = [mock_plugin_module]
    
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        # Specific plugin
        result = pluginutils.get_validate_plugin("MyValidate")
        assert result is not None
        
        # Default plugin
        mock_plugin_module.NodeManagerPlugin.name = "DefaultValidate"
        result = pluginutils.get_validate_plugin(None)
        assert result is not None

def test_get_release_plugin():
    mock_manager = MagicMock()
    mock_plugin_module = MagicMock()
    mock_plugin_module.NodeManagerPlugin.name = "MyRelease"
    mock_manager._plugins = [mock_plugin_module]
    
    with patch("node_manager.utils.get_manager", return_value=mock_manager):
        # Specific plugin
        result = pluginutils.get_release_plugin("MyRelease")
        assert result is not None
        
        # Default plugin
        mock_plugin_module.NodeManagerPlugin.name = "DefaultRelease"
        result = pluginutils.get_release_plugin(None)
        assert result is not None
