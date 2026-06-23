"""
Example: generate Nmap NSE script scaffolding with AIScriptGenerator.

The generator is template/heuristic-based: it builds NSE (Lua) scaffolding
from a target type, a set of vulnerability checks, and a stealth level.
The xss/sql_injection checks emit real HTTP probes; other checks are
clearly-marked TODO placeholders.

    python examples/ai_script_gen.py \
        --target-type web_server --vuln xss --vuln sql_injection -o web.nse
"""

import argparse
import sys
from pathlib import Path

# Allow running this file directly from a source checkout.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nmap_ai.ai.script_generator import AIScriptGenerator  # noqa: E402
from nmap_ai.utils.logger import get_logger  # noqa: E402

TARGET_TYPES = ["web_server", "network_device", "database", "general"]
STEALTH_LEVELS = ["low", "medium", "high"]


def main() -> None:
    parser = argparse.ArgumentParser(description="AI script generation example")
    parser.add_argument("--target-type", choices=TARGET_TYPES, default="general",
                        help="Type of target the script is for")
    parser.add_argument("--vuln", action="append", dest="vulnerabilities",
                        help="Vulnerability check to include (repeatable), "
                             "e.g. xss, sql_injection, weak_authentication")
    parser.add_argument("--stealth", choices=STEALTH_LEVELS, default="medium",
                        help="Stealth level (controls timing delays)")
    parser.add_argument("--output", "-o", help="Write the generated script to a file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()
    logger = get_logger("ai_script_gen", level="DEBUG" if args.verbose else "INFO")

    generator = AIScriptGenerator()
    logger.info(f"Generating {args.target_type} script "
                f"(vulns={args.vulnerabilities or 'none'}, stealth={args.stealth})")

    script = generator.create_script(
        target_type=args.target_type,
        vulnerabilities=args.vulnerabilities,
        stealth_level=args.stealth,
    )

    print("\n" + "=" * 60)
    print("GENERATED NMAP SCRIPT")
    print("=" * 60)
    print(script)
    print("=" * 60)

    if args.output:
        Path(args.output).write_text(script, encoding="utf-8")
        logger.info(f"Script saved to {args.output}")


def demonstrate_predefined_scripts() -> None:
    """Show short previews for a few representative script types."""
    generator = AIScriptGenerator()
    examples = [
        ("web_server", ["xss", "sql_injection"]),
        ("network_device", ["weak_authentication"]),
        ("database", ["sql_injection"]),
        ("general", None),
    ]

    print("\n" + "=" * 60)
    print("PREDEFINED SCRIPT EXAMPLES")
    print("=" * 60)
    for target_type, vulns in examples:
        print(f"\n--- {target_type} (vulns={vulns or 'none'}) ---")
        script = generator.create_script(target_type=target_type, vulnerabilities=vulns)
        lines = script.strip().split("\n")
        for line in lines[:12]:
            print(f"  {line}")
        if len(lines) > 12:
            print(f"  ... ({len(lines) - 12} more lines)")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Run with --help for options, or showing predefined examples:\n")
        demonstrate_predefined_scripts()
    else:
        main()
