import pytest
from pathlib import Path
from ..paths import (
    get_config_paths,
    get_base_config_path,
    get_query_config_path,
)


# ── GetConfigPaths ────────────────────────────────────────────────────────────

class TestGetConfigPaths:

    def test_returns_tuple_of_two(self):
        result = get_config_paths()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_both_elements_are_paths(self):
        base, query = get_config_paths()
        assert isinstance(base, Path)
        assert isinstance(query, Path)

    def test_base_config_filename_is_correct(self):
        base, _ = get_config_paths()
        assert base.suffix == ".json"

    def test_query_config_filename_is_correct(self):
        _, query = get_config_paths()
        assert query.suffix == ".json"

    def test_both_paths_share_same_parent(self):
        base, query = get_config_paths()
        assert base.parent == query.parent

    def test_paths_are_absolute(self):
        base, query = get_config_paths()
        assert base.is_absolute()
        assert query.is_absolute()


# ── GetBaseConfigPath ─────────────────────────────────────────────────────────

class TestGetBaseConfigPath:

    def test_returns_a_path(self):
        result = get_base_config_path()
        assert isinstance(result, Path)

    def test_matches_first_element_of_get_config_paths(self):
        result = get_base_config_path()
        assert result == get_config_paths()[0]


# ── GetQueryConfigPath ────────────────────────────────────────────────────────

class TestGetQueryConfigPath:

    def test_returns_a_path(self):
        result = get_query_config_path()
        assert isinstance(result, Path)

    def test_matches_second_element_of_get_config_paths(self):
        result = get_query_config_path()
        assert result == get_config_paths()[1]