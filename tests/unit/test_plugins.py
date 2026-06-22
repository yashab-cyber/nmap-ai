"""
Unit tests for the plugin system: default dirs, discovery, and loading the
shipped example plugin end-to-end.
"""
from pathlib import Path

import pytest

from nmap_ai.plugins import PluginManager, ReportPlugin, default_plugin_dirs

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples" / "plugins"


def test_default_plugin_dirs():
    dirs = default_plugin_dirs()
    assert Path.home() / ".nmap-ai" / "plugins" in dirs
    assert Path.cwd() / "plugins" in dirs


def test_manager_uses_defaults_when_unspecified():
    pm = PluginManager()
    assert pm.plugin_dirs == default_plugin_dirs()


def test_discover_finds_example():
    pm = PluginManager(plugin_dirs=[EXAMPLES_DIR])
    discovered = pm.discover_plugins()
    assert "markdown_report_plugin" in discovered


def test_discover_skips_missing_dirs(tmp_path):
    pm = PluginManager(plugin_dirs=[tmp_path / "does-not-exist"])
    assert pm.discover_plugins() == []


class TestExamplePlugin:
    @pytest.fixture
    def loaded(self):
        pm = PluginManager(plugin_dirs=[EXAMPLES_DIR])
        assert pm.load_plugin("markdown_report_plugin") is True
        yield pm
        pm.cleanup_all()

    @pytest.fixture
    def summary(self):
        return {
            "scan_id": "scan_1",
            "start_time": "t0",
            "duration": 2.0,
            "results": {
                "10.0.0.1": {"parsed": {"open_ports": [
                    {"port": 22, "protocol": "tcp", "name": "ssh",
                     "product": "OpenSSH", "version": "7.4"},
                ]}},
                "10.0.0.2": {"error": "host down"},
            },
        }

    def test_loaded_and_listed(self, loaded):
        assert loaded.get_plugin("markdown_report_plugin") is not None
        assert loaded.list_plugins(ReportPlugin) == ["markdown_report_plugin"]

    def test_metadata(self, loaded):
        plugin = loaded.get_plugin("markdown_report_plugin")
        assert plugin.metadata.name == "markdown_report"
        assert "md" in plugin.supported_formats

    def test_generate_report_content(self, loaded, summary):
        plugin = loaded.get_plugin("markdown_report_plugin")
        report = plugin.generate_report(summary, "md")
        assert "# NMAP-AI Scan Report" in report
        assert "scan_1" in report
        assert "10.0.0.1" in report
        assert "ssh" in report
        assert "host down" in report

    def test_generate_report_writes_file(self, loaded, summary, tmp_path):
        plugin = loaded.get_plugin("markdown_report_plugin")
        out = tmp_path / "report.md"
        plugin.generate_report(summary, "md", output_path=out)
        assert out.exists() and "# NMAP-AI Scan Report" in out.read_text(encoding="utf-8")

    def test_unsupported_format_raises(self, loaded, summary):
        plugin = loaded.get_plugin("markdown_report_plugin")
        with pytest.raises(ValueError, match="Unsupported format"):
            plugin.generate_report(summary, "pdf")
