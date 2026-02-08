# test_logging_factory.py
import pytest
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from logging.handlers import RotatingFileHandler
from src.utils.logging_factory import initialize_logging
from src.core.config_manager.config_models import BaseConfig


class TestInitializeLogging:
    def test_creates_log_directory(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(
            data_directory=tmp_path,
            default_file="test.csv",
            log_directory=log_dir,
            max_log_size=1000
        )
        
        initialize_logging(config, debug=False)
        
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_creates_debug_log_in_debug_mode(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=True)
        
        debug_log = log_dir / "debug.log"
        assert debug_log.exists()
    
    def test_creates_prod_log_in_production_mode(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        prod_log = log_dir / "prod.log"
        assert prod_log.exists()
    
    def test_debug_mode_sets_debug_level(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=True)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    def test_production_mode_sets_error_level(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR
    
    def test_uses_rotating_file_handler(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        handlers = [h for h in root_logger.handlers if isinstance(h, RotatingFileHandler)]
        assert len(handlers) > 0
    
    def test_max_bytes_from_config(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 5000)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert isinstance(handler, RotatingFileHandler)
        assert handler.maxBytes == 5000
    
    def test_backup_count_is_three(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert handler.backupCount == 3
    
    def test_formatter_includes_timestamp(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter
        assert formatter is not None
        assert '%(asctime)s' in formatter._fmt
    
    def test_formatter_includes_level_and_message(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter
        assert '%(levelname)s' in formatter._fmt
        assert '%(message)s' in formatter._fmt
    
    def test_clears_existing_handlers(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        root_logger = logging.getLogger()
        old_handler = logging.StreamHandler()
        root_logger.addHandler(old_handler)
        
        initialize_logging(config, debug=False)
        
        assert old_handler not in root_logger.handlers
    
    def test_creates_parent_directories(self, tmp_path):
        log_dir = tmp_path / "nested" / "logs" / "dir"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        assert log_dir.exists()
        assert (log_dir / "prod.log").exists()
    
    def test_logs_initialization_message(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=True)
        
        log_file = log_dir / "debug.log"
        assert log_file.exists()
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Logger initialized" in content
    
    def test_encoding_utf8(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert handler.encoding == 'utf-8'
    
    def test_default_max_log_size_if_missing(self, tmp_path):
        log_dir = tmp_path / "logs"
        
        # Create config without max_log_size (should use default)
        from dataclasses import dataclass
        @dataclass(frozen=True)
        class MinimalConfig:
            log_directory: Path
        
        config = MinimalConfig(log_directory=log_dir)
        
        initialize_logging(config, debug=False)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert handler.maxBytes == 100000
    
    def test_multiple_initializations(self, tmp_path):
        log_dir = tmp_path / "logs"
        config = BaseConfig(tmp_path, "test.csv", log_dir, 1000)
        
        initialize_logging(config, debug=False)
        first_handler_count = len(logging.getLogger().handlers)
        
        initialize_logging(config, debug=True)
        second_handler_count = len(logging.getLogger().handlers)
        
        assert first_handler_count == second_handler_count == 1