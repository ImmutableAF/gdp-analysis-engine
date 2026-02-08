# test_args_manager.py
import pytest
import sys
from unittest.mock import patch
from src.utils.args_manager import parse_cli_args


class TestParseCliArgs:
    def test_no_arguments(self):
        with patch('sys.argv', ['script.py']):
            args = parse_cli_args()
            
            assert args.debug is False
            assert args.fpath is None
    
    def test_debug_flag(self):
        with patch('sys.argv', ['script.py', '--debug']):
            args = parse_cli_args()
            
            assert args.debug is True
    
    def test_fpath_argument(self):
        with patch('sys.argv', ['script.py', '-fpath', '/path/to/file.csv']):
            args = parse_cli_args()
            
            assert args.fpath == '/path/to/file.csv'
    
    def test_both_arguments(self):
        with patch('sys.argv', ['script.py', '--debug', '-fpath', 'data.csv']):
            args = parse_cli_args()
            
            assert args.debug is True
            assert args.fpath == 'data.csv'
    
    def test_arguments_order_independent(self):
        with patch('sys.argv', ['script.py', '-fpath', 'file.csv', '--debug']):
            args = parse_cli_args()
            
            assert args.debug is True
            assert args.fpath == 'file.csv'
    
    def test_fpath_with_spaces(self):
        with patch('sys.argv', ['script.py', '-fpath', '/path/with spaces/file.csv']):
            args = parse_cli_args()
            
            assert args.fpath == '/path/with spaces/file.csv'
    
    def test_fpath_relative_path(self):
        with patch('sys.argv', ['script.py', '-fpath', '../data/file.csv']):
            args = parse_cli_args()
            
            assert args.fpath == '../data/file.csv'
    
    def test_fpath_absolute_path(self):
        with patch('sys.argv', ['script.py', '-fpath', '/absolute/path/file.csv']):
            args = parse_cli_args()
            
            assert args.fpath == '/absolute/path/file.csv'
    
    def test_debug_false_by_default(self):
        with patch('sys.argv', ['script.py', '-fpath', 'file.csv']):
            args = parse_cli_args()
            
            assert args.debug is False
    
    def test_invalid_flag_raises_error(self):
        with patch('sys.argv', ['script.py', '--invalid']):
            with pytest.raises(SystemExit):
                parse_cli_args()
    
    def test_fpath_without_value_raises_error(self):
        with patch('sys.argv', ['script.py', '-fpath']):
            with pytest.raises(SystemExit):
                parse_cli_args()