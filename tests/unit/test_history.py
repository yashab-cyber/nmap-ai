"""
Unit tests for the persistent scan-history store.
"""
import pytest

from nmap_ai.core.history import ScanHistoryStore, sqlite_url_to_path


@pytest.mark.parametrize("url,expected", [
    ("sqlite:///history.db", "history.db"),
    ("sqlite:////tmp/h.db", "/tmp/h.db"),
    ("sqlite:///:memory:", ":memory:"),
    ("/already/a/path.db", "/already/a/path.db"),
])
def test_sqlite_url_to_path(url, expected):
    assert sqlite_url_to_path(url) == expected


@pytest.fixture
def store(tmp_path):
    s = ScanHistoryStore(f"sqlite:///{tmp_path / 'h.db'}")
    yield s
    s.close()


def _summary(scan_id, targets):
    return {
        "scan_id": scan_id,
        "start_time": "t0",
        "end_time": "t1",
        "duration": 1.0,
        "targets": targets,
        "ports": "1-100",
        "arguments": "-sV",
        "ai_enabled": True,
        "results": {t: {"status": "success"} for t in targets},
    }


def test_save_and_get(store):
    store.save(_summary("s1", ["10.0.0.1"]))
    store.save(_summary("s2", ["10.0.0.2"]))
    rows = store.get()
    assert [r["scan_id"] for r in rows] == ["s1", "s2"]  # oldest-first
    assert store.count() == 2


def test_get_limit_returns_most_recent_in_order(store):
    for i in range(5):
        store.save(_summary(f"s{i}", [f"10.0.0.{i}"]))
    recent = store.get(limit=2)
    assert [r["scan_id"] for r in recent] == ["s3", "s4"]


def test_clear(store):
    store.save(_summary("s1", ["10.0.0.1"]))
    store.clear()
    assert store.count() == 0
    assert store.get() == []


def test_persists_across_store_instances(tmp_path):
    url = f"sqlite:///{tmp_path / 'h.db'}"
    s1 = ScanHistoryStore(url)
    s1.save(_summary("s1", ["10.0.0.1"]))
    s1.close()

    s2 = ScanHistoryStore(url)
    assert s2.count() == 1
    assert s2.get()[0]["scan_id"] == "s1"
    s2.close()


def test_memory_store_works(tmp_path):
    s = ScanHistoryStore("sqlite:///:memory:")
    s.save(_summary("s1", ["10.0.0.1"]))
    assert s.count() == 1
    s.close()
