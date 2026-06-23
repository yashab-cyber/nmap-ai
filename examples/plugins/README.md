# Example plugins

Working reference plugins for the NMAP-AI plugin system.

## Plugin directories

`PluginManager()` (with no arguments) searches these locations, in order:

| Directory | Purpose |
|---|---|
| `~/.nmap-ai/plugins/` | user-global plugins |
| `./plugins/` | project-local plugins (relative to the current working directory) |

To install a plugin, copy its `.py` file into one of those directories.

```bash
mkdir -p ~/.nmap-ai/plugins
cp markdown_report_plugin.py ~/.nmap-ai/plugins/
```

## Using a plugin

```python
from nmap_ai.plugins import PluginManager

pm = PluginManager()                      # uses the default dirs
print(pm.discover_plugins())              # ['markdown_report_plugin', ...]

pm.load_plugin('markdown_report_plugin')
plugin = pm.get_plugin('markdown_report_plugin')

markdown = plugin.generate_report(scan_summary, 'md')
print(markdown)
```

You can also point the manager at an explicit directory (e.g. this folder):

```python
from pathlib import Path
from nmap_ai.plugins import PluginManager

pm = PluginManager(plugin_dirs=[Path('examples/plugins')])
pm.load_plugin('markdown_report_plugin')
```

## Available examples

- **`markdown_report_plugin.py`** — a `ReportPlugin` that renders a scan
  summary (as produced by `NmapAIScanner.scan()`) into a Markdown report.

## Writing your own

Inherit from one of the base classes in `nmap_ai.plugins`
(`ScannerPlugin`, `ReportPlugin`, `AIPlugin`) and implement the abstract
methods — at minimum `metadata`, `initialize()`, and `cleanup()`, plus the
base-class-specific hooks. See `markdown_report_plugin.py` for a complete,
loadable example.
