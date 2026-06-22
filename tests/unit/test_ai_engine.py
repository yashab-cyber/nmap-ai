"""
Unit tests for AIEngine (the heuristic/rule-based scan engine).
"""
import pytest

from nmap_ai.core.ai_engine import AIEngine


@pytest.fixture
def engine():
    return AIEngine()


class TestOptimizeScanArguments:
    def test_small_scan_is_polite(self, engine):
        args = engine.optimize_scan_arguments(["10.0.0.1"], "1-100", "")
        assert "-T2" in args  # <=10 targets -> polite
        assert "-sV" in args  # service detection added when absent
        assert "-O" in args   # OS detection for small scans

    def test_medium_scan_timing(self, engine):
        targets = [f"10.0.0.{i}" for i in range(1, 21)]  # 20 targets
        args = engine.optimize_scan_arguments(targets, "1-100", "")
        assert "-T3" in args

    def test_large_scan_is_aggressive_and_skips_os(self, engine):
        targets = [f"10.0.{i}.{j}" for i in range(2) for j in range(60)]  # 120
        args = engine.optimize_scan_arguments(targets, "1-100", "")
        assert "-T4" in args
        assert "-O" not in args  # OS detection skipped for >50 targets

    def test_does_not_duplicate_existing_flags(self, engine):
        args = engine.optimize_scan_arguments(["10.0.0.1"], "1-100", "-sV -O")
        assert args.count("-sV") == 1
        assert args.count("-O") == 1

    def test_web_target_adds_http_scripts(self, engine):
        args = engine.optimize_scan_arguments(["web.example.com"], "80", "")
        assert "--script=http-*" in args

    def test_mixed_services_adds_safe_scripts(self, engine):
        args = engine.optimize_scan_arguments(["10.0.0.1"], "1-100", "")
        # plain IP -> not web/db -> mixed_services True -> safe scripts
        assert "--script=safe" in args


class TestAnalyzeTargets:
    def test_detects_web_and_db(self, engine):
        analysis = engine._analyze_targets(["www.example.com", "db-prod.example.com"])
        assert analysis["likely_web_servers"] is True
        assert analysis["likely_databases"] is True
        assert analysis["network_size"] == 2


class TestAnalyzeTargetResult:
    def _ports(self, *ports):
        return {"open_ports": [{"port": p, "name": "x"} for p in ports], "services": []}

    def test_high_risk_port_sets_high(self, engine):
        analysis = engine._analyze_target_result("h", self._ports(3389))
        assert analysis["risk_level"] == "high"
        assert "Immediate security review recommended" in analysis["recommendations"]

    def test_medium_risk_threshold(self, engine):
        analysis = engine._analyze_target_result("h", self._ports(25, 53, 80))
        assert analysis["risk_level"] == "medium"

    def test_telnet_flagged_unencrypted(self, engine):
        parsed = {"open_ports": [{"port": 23, "name": "telnet"}], "services": []}
        analysis = engine._analyze_target_result("h", parsed)
        types = [i["type"] for i in analysis["security_issues"]]
        assert "unencrypted_protocol" in types
        assert any("secure alternatives" in r for r in analysis["recommendations"])

    def test_clean_host_is_low_risk(self, engine):
        analysis = engine._analyze_target_result("h", self._ports(8081))
        assert analysis["risk_level"] == "low"


class TestEnhanceResults:
    def test_adds_analysis_and_insights(self, engine):
        results = {
            "results": {
                "10.0.0.1": {"parsed": {
                    "open_ports": [{"port": 23, "name": "telnet"}],
                    "services": ["telnet"],
                }},
                "10.0.0.2": {"error": "down"},
            }
        }
        enhanced = engine.enhance_results(results)
        assert "ai_analysis" in enhanced["results"]["10.0.0.1"]
        assert "ai_insights" in enhanced
        stats = enhanced["ai_insights"]["statistics"]
        assert stats["total_targets"] == 2
        assert stats["successful_scans"] == 1
        assert stats["scan_success_rate"] == 50.0


class TestCreateScanPlan:
    @pytest.mark.parametrize("profile,expected_timing", [
        ("fast", "T4"), ("thorough", "T3"), ("stealth", "T1"),
    ])
    def test_static_profiles(self, engine, profile, expected_timing):
        plan = engine.create_scan_plan("10.0.0.1", profile, [])
        assert plan["timing"] == expected_timing
        assert plan["ports"]
        assert "insights" in plan

    def test_adaptive_no_history(self, engine):
        plan = engine.create_scan_plan("10.0.0.1", "adaptive", [])
        assert plan["ports"] == "1-1000"
        assert "No historical data" in plan["insights"]["historical_context"]

    def test_adaptive_with_successful_history_expands(self, engine):
        history = [{"targets": ["10.0.0.1"], "results": {"10.0.0.1": {"parsed": {}}}}]
        plan = engine.create_scan_plan("10.0.0.1", "adaptive", history)
        assert plan["ports"] == "1-10000"
        assert "1 previous scans" in plan["insights"]["historical_context"]

    def test_adaptive_with_failed_history_shrinks(self, engine):
        history = [{"targets": ["10.0.0.1"], "results": {"10.0.0.1": {"error": "x"}}}]
        plan = engine.create_scan_plan("10.0.0.1", "adaptive", history)
        assert plan["ports"] == "1-100"


class TestEstimateScanDuration:
    def test_seconds(self, engine):
        assert "second" in engine._estimate_scan_duration({"ports": "1-100", "timing": "T4"})

    def test_minutes(self, engine):
        assert "minute" in engine._estimate_scan_duration({"ports": "1-65535", "timing": "T3"})

    def test_hours(self, engine):
        # (100000 / 100) * 4.0 (T1) = 4000s -> ~1.1 hours
        assert "hour" in engine._estimate_scan_duration({"ports": "1-100000", "timing": "T1"})

    def test_malformed_ports_falls_back(self, engine):
        # unparsable range -> default 1000 ports, should not raise
        assert engine._estimate_scan_duration({"ports": "abc-def", "timing": "T3"})
