import logging
import sys
import pytest
from pathlib import Path
from unittest.mock import patch
from logging.handlers import RotatingFileHandler

from src.util.cli_parser import parse_cli_args
from src.util.logging_setup import initialize_logging
from src.util.logging_contract import LogPolicy
from dataclasses import dataclass


# ── Fake config for logging tests ─────────────────────────────────────────────

@dataclass
class FakeLogConfig:  # pragma: no cover
    log_dir: Path
    max_log_size: int = 1000000


# ── ParseCliArgs ──────────────────────────────────────────────────────────────

class TestParseCliArgs:

    def test_debug_is_false_by_default(self):
        with patch.object(sys, "argv", ["prog"]):
            result = parse_cli_args()
        assert result.debug is False

    def test_debug_flag_sets_debug_to_true(self):
        with patch.object(sys, "argv", ["prog", "--debug"]):
            result = parse_cli_args()
        assert result.debug is True

    def test_file_path_defaults_to_provided_value(self):
        with patch.object(sys, "argv", ["prog"]):
            result = parse_cli_args(file_path=Path("data/gdp.xlsx"))
        assert result.file_path == Path("data/gdp.xlsx")

    def test_fp_flag_overrides_default_file_path(self):
        with patch.object(sys, "argv", ["prog", "--fp", "data/other.xlsx"]):
            result = parse_cli_args(file_path=Path("data/gdp.xlsx"))
        assert result.file_path == Path("data/other.xlsx")

    def test_file_path_is_none_when_not_provided(self):
        with patch.object(sys, "argv", ["prog"]):
            result = parse_cli_args()
        assert result.file_path is None

    def test_fp_value_is_returned_as_path(self):
        with patch.object(sys, "argv", ["prog", "--fp", "data/gdp.xlsx"]):
            result = parse_cli_args()
        assert isinstance(result.file_path, Path)

    def test_description_does_not_affect_parsed_result(self):
        with patch.object(sys, "argv", ["prog"]):
            result = parse_cli_args(description="My App")
        assert result.debug is False
        assert result.file_path is None

    def test_both_flags_together(self):
        with patch.object(sys, "argv", ["prog", "--debug", "--fp", "data/gdp.xlsx"]):
            result = parse_cli_args()
        assert result.debug is True
        assert result.file_path == Path("data/gdp.xlsx")


# ── LogPolicy ─────────────────────────────────────────────────────────────────

class TestLogPolicy:

    def test_object_with_required_attrs_satisfies_contract(self):
        config = FakeLogConfig(log_dir=Path("logs"))
        assert isinstance(config.log_dir, Path)
        assert isinstance(config.max_log_size, int)

    def test_log_dir_is_path(self):
        config = FakeLogConfig(log_dir=Path("logs"))
        assert isinstance(config.log_dir, Path)

    def test_max_log_size_is_int(self):
        config = FakeLogConfig(log_dir=Path("logs"), max_log_size=500000)
        assert config.max_log_size == 500000


# ── InitializeLogging ─────────────────────────────────────────────────────────

class TestInitializeLogging:

    @pytest.fixture(autouse=True)
    def reset_root_logger(self):
        root = logging.getLogger()
        original_handlers = root.handlers[:]
        original_level = root.level
        yield
        root.handlers = original_handlers
        root.setLevel(original_level)

    def test_creates_log_dir_if_missing(self, tmp_path):
        log_dir = tmp_path / "new_logs"
        config = FakeLogConfig(log_dir=log_dir)
        initialize_logging(config, debug=True)
        assert log_dir.exists()

    def test_debug_mode_creates_debug_log(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path)
        initialize_logging(config, debug=True)
        assert (tmp_path / "debug.log").exists()

    def test_prod_mode_creates_prod_log(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path)
        initialize_logging(config, debug=False)
        assert (tmp_path / "prod.log").exists()

    def test_debug_mode_sets_debug_level(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path)
        initialize_logging(config, debug=True)
        assert logging.getLogger().level == logging.DEBUG

    def test_prod_mode_sets_error_level(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path)
        initialize_logging(config, debug=False)
        assert logging.getLogger().level == logging.ERROR

    def test_adds_rotating_file_handler(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path)
        initialize_logging(config, debug=True)
        handlers = logging.getLogger().handlers
        assert any(isinstance(h, RotatingFileHandler) for h in handlers)

    def test_clears_existing_handlers(self, tmp_path):
        root = logging.getLogger()
        root.addHandler(logging.StreamHandler())
        root.addHandler(logging.StreamHandler())
        config = FakeLogConfig(log_dir=tmp_path)
        initialize_logging(config, debug=True)
        assert len(root.handlers) == 1

    def test_handler_uses_max_log_size(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path, max_log_size=500000)
        initialize_logging(config, debug=True)
        handler = next(h for h in logging.getLogger().handlers if isinstance(h, RotatingFileHandler))
        assert handler.maxBytes == 500000

    def test_handler_keeps_3_backups(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path)
        initialize_logging(config, debug=True)
        handler = next(h for h in logging.getLogger().handlers if isinstance(h, RotatingFileHandler))
        assert handler.backupCount == 3

    def test_returns_none(self, tmp_path):
        config = FakeLogConfig(log_dir=tmp_path)
        result = initialize_logging(config, debug=True)
        assert result is None