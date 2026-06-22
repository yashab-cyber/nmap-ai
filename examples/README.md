# Examples

Runnable examples for NMAP-AI. Each script is self-contained and adds the
project root to `sys.path`, so you can run it straight from a source
checkout.

## Contents

| Example | What it shows |
|---|---|
| [`basic_scan.py`](basic_scan.py) | Run a scan with `NmapAIScanner` and print/save the results |
| [`ai_script_gen.py`](ai_script_gen.py) | Generate NSE (Lua) script scaffolding with `AIScriptGenerator` |
| [`batch_scanning.py`](batch_scanning.py) | Scan many targets concurrently and write a JSON report |
| [`plugins/`](plugins/) | A working `ReportPlugin` + how the plugin system loads it (see [`plugins/README.md`](plugins/README.md)) |

## Prerequisites

```bash
pip install -r requirements.txt
nmap --version   # nmap must be installed for the scanning examples
```

`ai_script_gen.py` does **not** require nmap — it only generates script text.

## `basic_scan.py`

```bash
python examples/basic_scan.py --target scanme.nmap.org --ports 22,80
python examples/basic_scan.py --target 192.168.1.0/24 --no-ai -o scan.json
```

Options: `--target` (required), `--ports`, `--arguments` (extra raw nmap
args), `--no-ai` (disable the heuristic engine/optimization),
`--output/-o` (write the full summary as JSON), `--verbose/-v`.

The equivalent in code:

```python
from nmap_ai import NmapAIScanner

scanner = NmapAIScanner()
summary = scanner.scan("scanme.nmap.org", ports="22,80")

for target, result in summary["results"].items():
    parsed = result.get("parsed", {})
    for port in parsed.get("open_ports", []):
        print(target, port["port"], port.get("name"))
```

## `ai_script_gen.py`

```bash
# Preview several target types (no arguments)
python examples/ai_script_gen.py

# Generate a web_server script with HTTP-based checks
python examples/ai_script_gen.py \
    --target-type web_server --vuln xss --vuln sql_injection -o web.nse
```

Options: `--target-type` (`web_server`, `network_device`, `database`,
`general`), `--vuln` (repeatable; e.g. `xss`, `sql_injection`,
`weak_authentication`), `--stealth` (`low`/`medium`/`high`),
`--output/-o`, `--verbose/-v`.

The equivalent in code:

```python
from nmap_ai import AIScriptGenerator

generator = AIScriptGenerator()
script = generator.create_script(
    target_type="web_server",
    vulnerabilities=["xss", "sql_injection"],
    stealth_level="medium",
)
print(script)
```

> The generated scripts are NSE scaffolding. The `xss`/`sql_injection`
> checks emit real HTTP probes; other checks are clearly-marked TODO
> placeholders for the operator to complete.

## `batch_scanning.py`

```bash
# targets.txt: one host/IP/range per line ('#' comments allowed)
python examples/batch_scanning.py --targets-file targets.txt -o report.json
```

Options: `--targets-file/-f` (required), `--ports/-p`, `--max-concurrent`,
`--no-ai`, `--output/-o` (JSON report path), `--verbose/-v`.

## Plugins

See [`plugins/README.md`](plugins/README.md) for the plugin directories,
how to install a plugin, and a complete `ReportPlugin` example
([`plugins/markdown_report_plugin.py`](plugins/markdown_report_plugin.py)).

## Safety

⚠️ Only scan hosts you own or are explicitly authorized to test. The
public `scanme.nmap.org` host is provided by the Nmap project for
testing. Be mindful of rate limits and network impact.
