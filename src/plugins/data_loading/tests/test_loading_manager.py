import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

from ..loading_manager import load_data, _import_plugins
import src.plugins.data_loading.loading_manager as loading_manager_module


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_loaded_flag():
    loading_manager_module._loaded = False
    yield
    loading_manager_module._loaded = False


# ── ImportPlugins ─────────────────────────────────────────────────────────────

class TestImportPlugins:

    def test_sets_loaded_flag_to_true(self):
        with patch("src.plugins.data_loading.loading_manager.iter_modules", return_value=[]):
            _import_plugins()
        assert loading_manager_module._loaded is True

    def test_runs_only_once(self):
        with patch("src.plugins.data_loading.loading_manager.iter_modules", return_value=[]) as mock_iter:
            _import_plugins()
            _import_plugins()
        assert mock_iter.call_count == 1

    def test_skips_if_already_loaded(self):
        loading_manager_module._loaded = True
        with patch("src.plugins.data_loading.loading_manager.iter_modules") as mock_iter:
            _import_plugins()
        mock_iter.assert_not_called()

    def test_failed_import_is_skipped_silently(self):
        fake_module = [("", "bad_plugin", False)]
        with patch("src.plugins.data_loading.loading_manager.iter_modules", return_value=fake_module), \
             patch("src.plugins.data_loading.loading_manager.import_module", side_effect=Exception("fail")):
            _import_plugins()  # should not raise
        assert loading_manager_module._loaded is True

    def test_imports_each_discovered_module(self):
        fake_modules = [("", "plugin_a", False), ("", "plugin_b", False)]
        with patch("src.plugins.data_loading.loading_manager.iter_modules", return_value=fake_modules), \
             patch("src.plugins.data_loading.loading_manager.import_module") as mock_import:
            _import_plugins()
        assert mock_import.call_count == 2


# ── LoadData ──────────────────────────────────────────────────────────────────

class TestLoadData:

    def test_returns_dataframe(self):
        fake_df = pd.DataFrame({"col": [1, 2, 3]})
        mock_loader = MagicMock()
        mock_loader.load.return_value = fake_df
        with patch("src.plugins.data_loading.loading_manager._import_plugins"), \
             patch("src.plugins.data_loading.loading_manager.get_loader", return_value=mock_loader):
            result = load_data(Path("data.csv"))
        assert isinstance(result, pd.DataFrame)

    def test_delegates_to_correct_loader(self):
        fake_df = pd.DataFrame()
        mock_loader = MagicMock()
        mock_loader.load.return_value = fake_df
        source = Path("data.csv")
        with patch("src.plugins.data_loading.loading_manager._import_plugins"), \
             patch("src.plugins.data_loading.loading_manager.get_loader", return_value=mock_loader):
            load_data(source)
        mock_loader.load.assert_called_once_with(source)

    def test_calls_import_plugins_before_get_loader(self):
        call_order = []
        with patch("src.plugins.data_loading.loading_manager._import_plugins",
                   side_effect=lambda: call_order.append("import")), \
             patch("src.plugins.data_loading.loading_manager.get_loader",
                   side_effect=lambda s: call_order.append("get") or MagicMock(load=lambda p: pd.DataFrame())):
            load_data(Path("data.csv"))
        assert call_order[0] == "import"
        assert call_order[1] == "get"

    def test_raises_value_error_when_no_loader_found(self):
        with patch("src.plugins.data_loading.loading_manager._import_plugins"), \
             patch("src.plugins.data_loading.loading_manager.get_loader", side_effect=ValueError("no loader")):
            with pytest.raises(ValueError):
                load_data(Path("data.unknown"))