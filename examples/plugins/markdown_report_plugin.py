"""
Example NMAP-AI plugin: Markdown scan report.

A minimal but fully working ``ReportPlugin`` that renders a scan summary
(as produced by ``NmapAIScanner.scan()``) into a Markdown document.

To use it, copy this file into one of the default plugin directories:

    ~/.nmap-ai/plugins/      (user-global)
    ./plugins/               (project-local)

then load it via the plugin manager:

    from nmap_ai.plugins import PluginManager
    pm = PluginManager()                 # uses the default dirs
    pm.discover_plugins()                # -> ['markdown_report_plugin', ...]
    pm.load_plugin('markdown_report_plugin')
    plugin = pm.get_plugin('markdown_report_plugin')
    markdown = plugin.generate_report(scan_summary, 'md')
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nmap_ai.plugins import ReportPlugin, PluginMetadata


class MarkdownReportPlugin(ReportPlugin):
    """Render scan results as a Markdown report."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="markdown_report",
            version="1.0.0",
            description="Renders scan results as a Markdown report",
            author="NMAP-AI examples",
            license="MIT",
            dependencies=[],
            supported_platforms=["linux", "windows", "macos"],
        )

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def cleanup(self) -> bool:
        self._initialized = False
        return True

    @property
    def supported_formats(self) -> List[str]:
        return ["md", "markdown"]

    def generate_report(
        self,
        scan_results: Dict[str, Any],
        format_type: str,
        output_path: Optional[Path] = None,
    ) -> Union[str, bytes]:
        if not self.validate_format(format_type):
            raise ValueError(f"Unsupported format: {format_type}")

        lines: List[str] = ["# NMAP-AI Scan Report", ""]

        scan_id = scan_results.get("scan_id")
        if scan_id:
            lines.append(f"- **Scan ID:** {scan_id}")
        if scan_results.get("start_time"):
            lines.append(f"- **Started:** {scan_results['start_time']}")
        if scan_results.get("duration") is not None:
            lines.append(f"- **Duration:** {scan_results['duration']}s")
        lines.append("")

        results = scan_results.get("results", {})
        for target, result in results.items():
            lines.append(f"## {target}")
            if "error" in result:
                lines.append(f"- ⚠️ Error: {result['error']}")
                lines.append("")
                continue

            parsed = result.get("parsed", {})
            open_ports = parsed.get("open_ports", [])
            if not open_ports:
                lines.append("- No open ports found.")
                lines.append("")
                continue

            lines.append("")
            lines.append("| Port | Proto | Service | Product | Version |")
            lines.append("|------|-------|---------|---------|---------|")
            for p in open_ports:
                lines.append(
                    "| {port} | {proto} | {service} | {product} | {version} |".format(
                        port=p.get("port", ""),
                        proto=p.get("protocol", ""),
                        service=p.get("name", ""),
                        product=p.get("product", ""),
                        version=p.get("version", ""),
                    )
                )
            lines.append("")

        report = "\n".join(lines)

        if output_path is not None:
            Path(output_path).write_text(report, encoding="utf-8")

        return report
