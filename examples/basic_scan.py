"""
Basic example: run a scan with NmapAIScanner and print the results.

Requires nmap to be installed and network access to the target.

    python examples/basic_scan.py --target scanme.nmap.org --ports 22,80
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running this file directly from a source checkout.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nmap_ai.core.scanner import NmapAIScanner  # noqa: E402
from nmap_ai.utils.logger import get_logger  # noqa: E402


def print_results(summary: dict) -> None:
    """Pretty-print the parsed results from a scan summary."""
    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)

    for target, result in summary.get("results", {}).items():
        print(f"\nHost: {target}")
        if "error" in result:
            print(f"  Error: {result['error']}")
            continue

        parsed = result.get("parsed", {})
        print(f"  Status: {parsed.get('status', 'unknown')}")

        open_ports = parsed.get("open_ports", [])
        if not open_ports:
            print("  No open ports found.")
            continue

        print("  Open ports:")
        for p in open_ports:
            service = p.get("name", "unknown")
            banner = " ".join(x for x in (p.get("product"), p.get("version")) if x)
            extra = f" ({banner})" if banner else ""
            print(f"    {p.get('port'):>5}/{p.get('protocol', 'tcp')} "
                  f"{p.get('state', ''):<6} {service}{extra}")

        # AI/heuristic analysis is attached when ai_enabled (the default).
        analysis = result.get("ai_analysis")
        if analysis:
            print(f"  Risk level: {analysis.get('risk_level', 'unknown')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Basic NMAP-AI scan example")
    parser.add_argument("--target", required=True, help="Target IP, host, or range")
    parser.add_argument("--ports", default="22,80,443", help="Ports to scan")
    parser.add_argument("--arguments", default="", help="Extra raw nmap arguments")
    parser.add_argument("--no-ai", action="store_true",
                        help="Disable the heuristic AI engine / optimization")
    parser.add_argument("--output", "-o", help="Write the full summary to a JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()
    logger = get_logger("basic_scan", level="DEBUG" if args.verbose else "INFO")

    try:
        scanner = NmapAIScanner(ai_enabled=not args.no_ai)
        logger.info(f"Scanning {args.target} (ports {args.ports})")

        summary = scanner.scan(
            args.target,
            ports=args.ports,
            arguments=args.arguments,
            ai_optimize=not args.no_ai,
        )

        print_results(summary)
        print(f"\nScan completed in {summary.get('duration', 0):.2f}s")

        if args.output:
            Path(args.output).write_text(
                json.dumps(summary, indent=2, default=str), encoding="utf-8"
            )
            logger.info(f"Summary written to {args.output}")

    except KeyboardInterrupt:
        logger.info("Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
