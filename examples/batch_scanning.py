"""
Example: batch-scan many targets concurrently and write a JSON report.

Reads targets from a file (one host/IP/range per line; blank lines and
lines starting with '#' are ignored), scans them concurrently via
NmapAIScanner.async_scan, prints a summary, and writes a JSON report.

Requires nmap installed and network access.

    python examples/batch_scanning.py --targets-file targets.txt -o report.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Allow running this file directly from a source checkout.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nmap_ai.core.scanner import NmapAIScanner  # noqa: E402
from nmap_ai.utils.logger import get_logger  # noqa: E402

logger = get_logger("batch_scanning")


def load_targets(filepath: str) -> List[str]:
    """Load scan targets from a file (skips blanks and '#' comments)."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Targets file not found: {filepath}")
    targets = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    logger.info(f"Loaded {len(targets)} targets from {filepath}")
    return targets


def summarize(results: dict) -> None:
    """Print a one-line summary per target."""
    print("\n" + "=" * 60)
    print("BATCH SCAN SUMMARY")
    print("=" * 60)
    for target, result in results.items():
        if "error" in result:
            print(f"  {target:<24} ERROR: {result['error']}")
            continue
        open_ports = result.get("parsed", {}).get("open_ports", [])
        ports = ", ".join(str(p.get("port")) for p in open_ports) or "none"
        print(f"  {target:<24} open: {ports}")


def main() -> None:
    parser = argparse.ArgumentParser(description="NMAP-AI batch scanning example")
    parser.add_argument("--targets-file", "-f", required=True,
                        help="File with targets, one per line")
    parser.add_argument("--ports", "-p", default="1-1000", help="Port range to scan")
    parser.add_argument("--max-concurrent", type=int, default=5,
                        help="Maximum concurrent scans")
    parser.add_argument("--no-ai", action="store_true",
                        help="Disable the heuristic AI engine")
    parser.add_argument("--output", "-o", default="batch_report.json",
                        help="JSON report output path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel("DEBUG")

    try:
        targets = load_targets(args.targets_file)
        if not targets:
            logger.error("No targets to scan")
            sys.exit(1)

        scanner = NmapAIScanner(ai_enabled=not args.no_ai)
        start = datetime.now()
        scan = scanner.async_scan(
            targets, ports=args.ports, max_concurrent=args.max_concurrent
        )
        duration = (datetime.now() - start).total_seconds()

        results = scan.get("results", {})
        summarize(results)

        failed = sum(1 for r in results.values() if "error" in r)
        print(f"\nScanned {len(results)} targets in {duration:.2f}s "
              f"({len(results) - failed} ok, {failed} failed)")

        report = {
            "generated": datetime.now().isoformat(),
            "duration_seconds": duration,
            "ports": args.ports,
            **scan,
        }
        Path(args.output).write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )
        logger.info(f"Report written to {args.output}")

    except KeyboardInterrupt:
        logger.info("Batch scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Batch scan failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
