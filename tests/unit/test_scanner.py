"""
Unit tests for NmapAIScanner.

The real ``nmap.PortScanner`` is mocked so these tests run without nmap
installed and without touching the network.
"""
import csv
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

from nmap_ai.core.scanner import NmapAIScanner


@pytest.fixture
def scanner(tmp_path):
    """A scanner with PortScanner mocked, AI disabled, and an isolated DB."""
    db_url = f"sqlite:///{tmp_path / 'history.db'}"
    with patch("nmap_ai.core.scanner.nmap.PortScanner"):
        yield NmapAIScanner(ai_enabled=False, db_url=db_url)


@pytest.fixture
def sample_summary():
    """A representative scan-summary dict as produced by scan()."""
    return {
        "scan_id": "scan_1",
        "start_time": "t0",
        "end_time": "t1",
        "duration": 1.5,
        "targets": ["192.168.1.1", "10.0.0.9"],
        "ports": "1-100",
        "arguments": "-sV",
        "ai_enabled": False,
        "results": {
            "192.168.1.1": {
                "status": "success",
                "parsed": {
                    "status": "up",
                    "open_ports": [
                        {"port": 22, "protocol": "tcp", "state": "open",
                         "name": "ssh", "product": "OpenSSH", "version": "7.4"},
                        {"port": 80, "protocol": "tcp", "state": "open",
                         "name": "http", "product": "Apache", "version": "2.4.6"},
                    ],
                },
            },
            "10.0.0.9": {"error": "host down"},
        },
    }


class TestExporters:
    def test_export_csv(self, scanner, sample_summary, tmp_path):
        out = tmp_path / "out.csv"
        scanner._export_csv(sample_summary, out)

        rows = list(csv.DictReader(out.open(newline="")))
        # two open ports + one errored host row
        assert len(rows) == 3
        assert rows[0]["target"] == "192.168.1.1"
        assert rows[0]["port"] == "22"
        assert rows[0]["service"] == "ssh"
        assert any(r["error"] == "host down" for r in rows)

    def test_export_xml_is_valid(self, scanner, sample_summary, tmp_path):
        out = tmp_path / "out.xml"
        scanner._export_xml(sample_summary, out)

        root = ET.parse(out).getroot()
        assert root.tag == "nmapai_scan"
        assert root.get("scan_id") == "scan_1"
        hosts = root.find("hosts").findall("host")
        assert len(hosts) == 2
        ports = hosts[0].find("ports").findall("port")
        assert {p.get("portid") for p in ports} == {"22", "80"}
        # errored host carries an <error> element
        assert hosts[1].get("status") == "error"
        assert hosts[1].find("error").text == "host down"

    def test_save_results_dispatch(self, scanner, sample_summary, tmp_path):
        for fmt, ext in (("json", "json"), ("xml", "xml"), ("csv", "csv")):
            out = tmp_path / f"out.{ext}"
            scanner._save_results(sample_summary, str(out), fmt)
            assert out.exists() and out.stat().st_size > 0

    def test_save_results_unknown_format(self, scanner, sample_summary, tmp_path):
        with pytest.raises(ValueError, match="Unsupported output format"):
            scanner._save_results(sample_summary, str(tmp_path / "x.txt"), "txt")


class TestScan:
    def test_scan_happy_path(self, scanner):
        scanner.nm.scan = MagicMock()
        scanner.nm.all_hosts = MagicMock(return_value=["127.0.0.1"])
        scanner.nm.command_line = MagicMock(return_value="nmap -p 1-100 127.0.0.1")
        scanner.nm.__getitem__ = MagicMock(return_value={
            "tcp": {22: {"state": "open", "name": "ssh"}},
        })

        summary = scanner.scan("127.0.0.1", ports="1-100", ai_optimize=False)

        assert summary["targets"] == ["127.0.0.1"]
        assert "127.0.0.1" in summary["results"]
        assert summary["results"]["127.0.0.1"]["status"] == "success"
        # recorded in history
        assert len(scanner.get_scan_history()) == 1

    def test_scan_invalid_target(self, scanner):
        with pytest.raises(ValueError, match="Invalid target"):
            scanner.scan("invalid target with spaces")

    def test_scan_invalid_ports(self, scanner):
        with pytest.raises(ValueError, match="Invalid port"):
            scanner.scan("127.0.0.1", ports="not-ports!!")


def _wire_mock_scan(scanner, host="127.0.0.1"):
    scanner.nm.scan = MagicMock()
    scanner.nm.all_hosts = MagicMock(return_value=[host])
    scanner.nm.command_line = MagicMock(return_value=f"nmap {host}")
    scanner.nm.__getitem__ = MagicMock(return_value={
        "tcp": {22: {"state": "open", "name": "ssh"}},
    })


class TestHistoryPersistence:
    def test_history_survives_new_instance(self, tmp_path):
        """A fresh scanner (new process) sees scans persisted earlier."""
        db_url = f"sqlite:///{tmp_path / 'history.db'}"

        with patch("nmap_ai.core.scanner.nmap.PortScanner"):
            first = NmapAIScanner(ai_enabled=False, db_url=db_url)
        _wire_mock_scan(first)
        first.scan("127.0.0.1", ports="1-100", ai_optimize=False)
        first.history_store.close()

        # Simulate a brand new process: a separate scanner over the same DB.
        with patch("nmap_ai.core.scanner.nmap.PortScanner"):
            second = NmapAIScanner(ai_enabled=False, db_url=db_url)
        history = second.get_scan_history()
        assert len(history) == 1
        assert history[0]["targets"] == ["127.0.0.1"]

    def test_clear_history(self, scanner):
        _wire_mock_scan(scanner)
        scanner.scan("127.0.0.1", ports="1-100", ai_optimize=False)
        assert len(scanner.get_scan_history()) == 1
        scanner.clear_scan_history()
        assert scanner.get_scan_history() == []

    def test_limit_returns_recent(self, scanner):
        _wire_mock_scan(scanner)
        for _ in range(3):
            scanner.scan("127.0.0.1", ports="1-100", ai_optimize=False)
        assert len(scanner.get_scan_history()) == 3
        assert len(scanner.get_scan_history(limit=2)) == 2
