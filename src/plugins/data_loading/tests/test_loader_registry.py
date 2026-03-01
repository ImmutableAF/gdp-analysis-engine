import pytest
from pathlib import Path

from ..loader_registry import register_plugin, get_loader, _loaders
from ..loader_interface import DataLoader


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_loaders():
    _loaders.clear()
    yield
    _loaders.clear()


# ── Fake loaders for testing ──────────────────────────────────────────────────

class FakeCsvLoader(DataLoader):  # pragma: no cover
    def supports(self, source: Path) -> bool:
        return source.suffix.lower() == ".csv"
    def load(self, source: Path):
        pass


class FakeXlsxLoader(DataLoader):  # pragma: no cover
    def supports(self, source: Path) -> bool:
        return source.suffix.lower() == ".xlsx"
    def load(self, source: Path):
        pass


class FakeNeverLoader(DataLoader):  # pragma: no cover
    def supports(self, source: Path) -> bool:
        return False
    def load(self, source: Path):
        pass


# ── RegisterPlugin ────────────────────────────────────────────────────────────

class TestRegisterPlugin:

    def test_registers_a_valid_subclass(self):
        register_plugin(FakeCsvLoader)
        assert len(_loaders) == 1

    def test_registered_instance_is_correct_type(self):
        register_plugin(FakeCsvLoader)
        assert isinstance(_loaders[0], FakeCsvLoader)

    def test_returns_original_class_unchanged(self):
        result = register_plugin(FakeCsvLoader)
        assert result is FakeCsvLoader

    def test_multiple_loaders_are_all_registered(self):
        register_plugin(FakeCsvLoader)
        register_plugin(FakeXlsxLoader)
        assert len(_loaders) == 2

    def test_registration_order_is_preserved(self):
        register_plugin(FakeCsvLoader)
        register_plugin(FakeXlsxLoader)
        assert isinstance(_loaders[0], FakeCsvLoader)
        assert isinstance(_loaders[1], FakeXlsxLoader)

    def test_dataloader_itself_is_not_registered(self):
        register_plugin(DataLoader)
        assert len(_loaders) == 0

    def test_decorator_syntax_works(self):
        @register_plugin
        class InlineLoader(DataLoader):
            def supports(self, source: Path) -> bool:
                return True
            def load(self, source: Path):
                pass
        loader = get_loader(Path("anything.xyz"))
        loader.load(Path("anything.xyz"))
        assert len(_loaders) == 1


# ── GetLoader ─────────────────────────────────────────────────────────────────

class TestGetLoader:

    def test_returns_matching_loader(self):
        register_plugin(FakeCsvLoader)
        result = get_loader(Path("data.csv"))
        assert isinstance(result, FakeCsvLoader)

    def test_returns_first_matching_loader(self):
        register_plugin(FakeCsvLoader)
        register_plugin(FakeXlsxLoader)
        result = get_loader(Path("data.csv"))
        assert isinstance(result, FakeCsvLoader)

    def test_returns_second_loader_when_first_does_not_match(self):
        register_plugin(FakeCsvLoader)
        register_plugin(FakeXlsxLoader)
        result = get_loader(Path("data.xlsx"))
        assert isinstance(result, FakeXlsxLoader)

    def test_raises_value_error_when_no_loader_matches(self):
        register_plugin(FakeNeverLoader)
        with pytest.raises(ValueError):
            get_loader(Path("data.csv"))

    def test_raises_value_error_when_no_loaders_registered(self):
        with pytest.raises(ValueError):
            get_loader(Path("data.csv"))

    def test_error_message_contains_source(self):
        with pytest.raises(ValueError, match="data.csv"):
            get_loader(Path("data.csv"))