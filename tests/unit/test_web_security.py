"""
Tests for web secret-key handling (env override + fail-fast on default).
"""
import pytest

from nmap_ai.config import NmapAIConfig, DEFAULT_SECRET_KEY
from nmap_ai.web.main import resolve_secret_key, secret_key_error, web_main, get_config


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    monkeypatch.delenv("NMAP_AI_SECRET_KEY", raising=False)


def _config(debug=False, secret_key=DEFAULT_SECRET_KEY):
    cfg = NmapAIConfig()
    cfg.web.debug = debug
    cfg.web.secret_key = secret_key
    return cfg


class TestResolveSecretKey:
    def test_env_overrides_config(self, monkeypatch):
        monkeypatch.setenv("NMAP_AI_SECRET_KEY", "from-env")
        assert resolve_secret_key(_config(secret_key="from-config")) == "from-env"

    def test_falls_back_to_config(self):
        assert resolve_secret_key(_config(secret_key="from-config")) == "from-config"


class TestSecretKeyError:
    def test_default_key_non_debug_is_rejected(self):
        err = secret_key_error(_config(debug=False, secret_key=DEFAULT_SECRET_KEY))
        assert err is not None
        assert "NMAP_AI_SECRET_KEY" in err

    def test_debug_mode_allows_default(self):
        assert secret_key_error(_config(debug=True)) is None

    def test_env_key_allows_start(self, monkeypatch):
        monkeypatch.setenv("NMAP_AI_SECRET_KEY", "a-strong-secret")
        assert secret_key_error(_config(debug=False)) is None

    def test_config_key_allows_start(self):
        assert secret_key_error(_config(debug=False, secret_key="set-in-config")) is None


class TestWebMainFailFast:
    def test_web_main_exits_on_default_key(self, monkeypatch, capsys):
        cfg = get_config()
        monkeypatch.setattr(cfg.web, "debug", False)
        monkeypatch.setattr(cfg.web, "secret_key", DEFAULT_SECRET_KEY)

        with pytest.raises(SystemExit) as exc:
            web_main()
        assert exc.value.code != 0
        assert "default secret key" in capsys.readouterr().err
