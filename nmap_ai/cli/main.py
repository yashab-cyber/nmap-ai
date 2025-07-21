"""
CLI interface for NMAP-AI
"""

import click
import json
import sys
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel

from ..core.scanner import NmapAIScanner
from ..config import get_config
from ..utils.logger import get_logger


console = Console()
logger = get_logger(__name__)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', help='Configuration file path')
@click.pass_context
def cli(ctx, debug, config):
    """NMAP-AI: AI-Powered Network Scanning & Automation"""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    ctx.obj['CONFIG'] = config
    
    if debug:
        console.print("[yellow]Debug mode enabled[/yellow]")


@cli.command()
@click.argument('targets', nargs=-1, required=True)
@click.option('--ports', '-p', help='Port specification (e.g., 1-1000, 80,443)')
@click.option('--arguments', '-A', help='Additional nmap arguments')
@click.option('--ai-mode', type=click.Choice(['smart', 'fast', 'thorough', 'stealth']), 
              default='smart', help='AI scanning mode')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'xml', 'csv']), 
              default='json', help='Output format')
@click.option('--ai-optimize/--no-ai-optimize', default=True, help='Use AI optimization')
@click.option('--async-scan', is_flag=True, help='Use asynchronous scanning')
@click.option('--max-concurrent', type=int, default=10, help='Max concurrent scans for async mode')
def scan(targets, ports, arguments, ai_mode, output, output_format, ai_optimize, async_scan, max_concurrent):
    """Perform network scan on specified targets."""
    
    console.print(Panel.fit(
        f"[bold blue]NMAP-AI Scanner[/bold blue]\n"
        f"Targets: {', '.join(targets)}\n"
        f"AI Mode: {ai_mode}\n"
        f"AI Optimization: {'Enabled' if ai_optimize else 'Disabled'}"
    ))
    
    try:
        scanner = NmapAIScanner(ai_enabled=True)
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning...", total=len(targets))
            
            if async_scan:
                results = scanner.async_scan(
                    targets=list(targets),
                    ports=ports,
                    arguments=arguments,
                    max_concurrent=max_concurrent
                )
            else:
                results = scanner.scan(
                    targets=list(targets),
                    ports=ports,
                    arguments=arguments,
                    ai_optimize=ai_optimize
                )
            
            progress.update(task, completed=len(targets))
        
        # Display results
        _display_scan_results(results)
        
        # Save results if output specified
        if output:
            _save_scan_results(results, output, output_format)
            console.print(f"[green]Results saved to {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('target')
@click.option('--vulnerability', '-v', multiple=True, help='Vulnerability types to check')
@click.option('--target-type', type=click.Choice(['web_server', 'network_device', 'database', 'general']), 
              default='general', help='Target type')
@click.option('--stealth-level', type=click.Choice(['low', 'medium', 'high']), 
              default='medium', help='Stealth level')
@click.option('--output', '-o', help='Output script file')
def generate_script(target, vulnerability, target_type, stealth_level, output):
    """Generate AI-powered Nmap script."""
    
    console.print(Panel.fit(
        f"[bold green]AI Script Generator[/bold green]\n"
        f"Target: {target}\n"
        f"Type: {target_type}\n"
        f"Vulnerabilities: {', '.join(vulnerability) if vulnerability else 'General'}\n"
        f"Stealth Level: {stealth_level}"
    ))
    
    try:
        scanner = NmapAIScanner(ai_enabled=True)
        
        # Prepare target info
        target_info = {
            'target': target,
            'type': target_type,
            'vulnerabilities': list(vulnerability) if vulnerability else [],
            'stealth_level': stealth_level
        }
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating script...", total=1)
            
            script_content = scanner.generate_ai_script(
                target_info=target_info,
                script_type=target_type,
                requirements=list(vulnerability) if vulnerability else None
            )
            
            progress.update(task, completed=1)
        
        # Display generated script
        console.print(Panel(script_content, title="Generated Nmap Script", border_style="green"))
        
        # Save script if output specified
        if output:
            with open(output, 'w') as f:
                f.write(script_content)
            console.print(f"[green]Script saved to {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('targets_file')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'xml', 'csv']), 
              default='json', help='Output format')
@click.option('--max-concurrent', type=int, default=20, help='Maximum concurrent scans')
def batch(targets_file, output, output_format, max_concurrent):
    """Perform batch scanning from a targets file."""
    
    console.print(Panel.fit(
        f"[bold yellow]Batch Scanner[/bold yellow]\n"
        f"Targets File: {targets_file}\n"
        f"Max Concurrent: {max_concurrent}\n"
        f"Output Format: {output_format}"
    ))
    
    try:
        scanner = NmapAIScanner(ai_enabled=True)
        
        results = scanner.batch_scan(
            targets_file=targets_file,
            output_format=output_format,
            output_file=output
        )
        
        console.print(f"[green]Batch scan completed. Scanned {len(results.get('results', {}))} targets.[/green]")
        
        if output:
            console.print(f"[green]Results saved to {output}[/green]")
        else:
            _display_scan_results(results)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('target')
@click.option('--profile', type=click.Choice(['adaptive', 'fast', 'thorough', 'stealth']), 
              default='adaptive', help='Smart scan profile')
@click.option('--learn/--no-learn', default=True, help='Learn from previous scans')
def smart_scan(target, profile, learn):
    """Perform AI-powered smart scan."""
    
    console.print(Panel.fit(
        f"[bold magenta]Smart Scanner[/bold magenta]\n"
        f"Target: {target}\n"
        f"Profile: {profile}\n"
        f"Learning: {'Enabled' if learn else 'Disabled'}"
    ))
    
    try:
        scanner = NmapAIScanner(ai_enabled=True)
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Smart scanning...", total=1)
            
            results = scanner.smart_scan(
                target=target,
                scan_profile=profile,
                learn_from_previous=learn
            )
            
            progress.update(task, completed=1)
        
        # Display results with AI insights
        _display_scan_results(results)
        
        if 'ai_insights' in results:
            console.print(Panel(
                json.dumps(results['ai_insights'], indent=2),
                title="AI Insights",
                border_style="cyan"
            ))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--limit', type=int, help='Limit number of results')
def history(limit):
    """Show scan history."""
    
    try:
        scanner = NmapAIScanner(ai_enabled=True)
        scan_history = scanner.get_scan_history(limit=limit)
        
        if not scan_history:
            console.print("[yellow]No scan history found.[/yellow]")
            return
        
        table = Table(title="Scan History")
        table.add_column("Scan ID", style="cyan")
        table.add_column("Start Time", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Targets", style="blue")
        table.add_column("Status", style="red")
        
        for scan in scan_history:
            table.add_row(
                scan.get('scan_id', 'N/A'),
                scan.get('start_time', 'N/A'),
                f"{scan.get('duration', 0):.2f}s",
                str(len(scan.get('targets', []))),
                "Success" if 'error' not in scan else "Error"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def _display_scan_results(results):
    """Display scan results in a formatted table."""
    if 'results' not in results:
        console.print("[yellow]No results to display.[/yellow]")
        return
    
    table = Table(title="Scan Results")
    table.add_column("Target", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Open Ports", style="yellow")
    table.add_column("Services", style="blue")
    
    for target, result in results['results'].items():
        if 'error' in result:
            table.add_row(target, "Error", result.get('error', 'Unknown error'), "N/A")
        else:
            parsed = result.get('parsed', {})
            open_ports = parsed.get('open_ports', [])
            services = parsed.get('services', [])
            
            table.add_row(
                target,
                "Success",
                ', '.join(map(str, open_ports[:5])) + ('...' if len(open_ports) > 5 else ''),
                ', '.join(services[:3]) + ('...' if len(services) > 3 else '')
            )
    
    console.print(table)


def _save_scan_results(results, output_file, format):
    """Save scan results to file."""
    if format == 'json':
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)


def cli_main(args=None):
    """Main CLI entry point."""
    try:
        cli(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if get_config().debug:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    cli_main()
