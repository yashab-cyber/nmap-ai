"""
Unit tests for configuration management.
"""

from nmap_ai.config import (
    NmapAIConfig, AIConfig, ScanConfig, ConfigManager, get_config,
)


class TestDefaults:
    def test_nested_dataclasses_present(self):
        cfg = NmapAIConfig()
        assert isinstance(cfg.ai, AIConfig)
        assert isinstance(cfg.scanning, ScanConfig)
        assert cfg.scanning.default_ports == "1-1000"

    def test_instances_are_independent(self):
        """Regression guard for commit c61d49f (field(default_factory=...)).

        With a plain mutable default, all instances would share the same
        nested config objects; mutating one would leak into the others.
        """
        a = NmapAIConfig()
        b = NmapAIConfig()
        assert a.ai is not b.ai
        assert a.scanning is not b.scanning

        a.scanning.default_ports = "1-65535"
        assert b.scanning.default_ports == "1-1000"


class TestRoundTrip:
    def test_yaml_roundtrip_equal(self, tmp_path):
        path = tmp_path / "config.yml"
        mgr = ConfigManager(config_file=str(path))
        mgr.config.scanning.default_ports = "1-2000"
        mgr.config.web.port = 9090
        mgr.config.log_level = "DEBUG"
        mgr.save_config()

        assert path.exists()

        reloaded = ConfigManager(config_file=str(path))
        assert reloaded.config == mgr.config
        assert reloaded.config.scanning.default_ports == "1-2000"
        assert reloaded.config.web.port == 9090
        assert reloaded.config.log_level == "DEBUG"

    def test_json_roundtrip_equal(self, tmp_path):
        path = tmp_path / "config.json"
        mgr = ConfigManager(config_file=str(path))
        mgr.config.database.url = "sqlite:///custom.db"
        mgr.save_config()

        reloaded = ConfigManager(config_file=str(path))
        assert reloaded.config == mgr.config
        assert reloaded.config.database.url == "sqlite:///custom.db"

    def test_unknown_keys_are_ignored(self, tmp_path):
        path = tmp_path / "config.yml"
        path.write_text("scanning:\n  default_ports: '1-50'\n  bogus_key: 123\n")
        mgr = ConfigManager(config_file=str(path))
        assert mgr.config.scanning.default_ports == "1-50"
        assert not hasattr(mgr.config.scanning, "bogus_key")


class TestManagerOps:
    def test_update_config(self, tmp_path):
        mgr = ConfigManager(config_file=str(tmp_path / "c.yml"))
        mgr.update_config(scanning={"retries": 5}, web={"port": 1234})
        assert mgr.config.scanning.retries == 5
        assert mgr.config.web.port == 1234

    def test_reset_to_defaults(self, tmp_path):
        mgr = ConfigManager(config_file=str(tmp_path / "c.yml"))
        mgr.config.scanning.retries = 99
        mgr.reset_to_defaults()
        assert mgr.config.scanning.retries == ScanConfig().retries

    def test_global_get_config_returns_config(self):
        assert isinstance(get_config(), NmapAIConfig)
