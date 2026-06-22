"""
Unit tests for AIScriptGenerator.

These verify that generated NSE scripts are real, syntactically valid Lua
(not stub placeholders). The Lua syntax check uses the optional `luaparser`
package and is skipped if it is not installed.
"""
import pytest

from nmap_ai.ai.script_generator import AIScriptGenerator


@pytest.fixture
def generator():
    return AIScriptGenerator()


# (target_type, vulnerabilities, stealth_level)
SCRIPT_CASES = [
    ("web_server", ["xss", "sql_injection"], "medium"),
    ("web_server", ["xss"], "high"),
    ("web_server", ["sql_injection"], "low"),
    ("general", None, "medium"),
    ("database", ["sql_injection", "weak_authentication"], "high"),
    ("network_device", ["weak_authentication"], "low"),
]


@pytest.mark.parametrize("target_type,vulns,stealth", SCRIPT_CASES)
def test_generated_script_is_valid_lua(generator, target_type, vulns, stealth):
    ast = pytest.importorskip("luaparser.ast")
    script = generator.create_script(
        target_type=target_type, vulnerabilities=vulns, stealth_level=stealth
    )
    # Raises luaparser.ast.SyntaxException on malformed Lua.
    ast.parse(script)


def test_no_stub_placeholders_for_http_checks(generator):
    script = generator.create_script(
        target_type="web_server",
        vulnerabilities=["xss", "sql_injection"],
        stealth_level="medium",
    )
    assert "Add actual test logic here" not in script


def test_xss_and_sqli_emit_real_http_requests(generator):
    script = generator.create_script(
        target_type="web_server",
        vulnerabilities=["xss", "sql_injection"],
        stealth_level="medium",
    )
    assert "http.get(host, port" in script
    assert "url.escape" in script
    assert 'require "http"' in script
    assert 'require "url"' in script


def test_medium_stealth_avoids_float_math_random(generator):
    # math.random(float, float) raises under Lua 5.3 (nmap's runtime).
    script = generator.create_script(
        target_type="general", vulnerabilities=None, stealth_level="medium"
    )
    assert "math.random(0.5" not in script
    assert "math.random()" in script
