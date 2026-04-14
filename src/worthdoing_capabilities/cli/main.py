import json
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path

app = typer.Typer(
    name="wdcap",
    help="WorthDoing AI — Capability Package CLI",
    no_args_is_help=True,
)
console = Console()


@app.command()
def list(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    tag: str = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """List all registered capabilities."""
    from worthdoing_capabilities import CapabilityRuntime
    runtime = CapabilityRuntime()

    capabilities = runtime.registry.list_all()
    if category:
        capabilities = [c for c in capabilities if c.category == category]
    if tag:
        capabilities = [c for c in capabilities if tag in c.tags]

    table = Table(title="WorthDoing AI — Capabilities", show_lines=True)
    table.add_column("Name", style="cyan bold")
    table.add_column("Version", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="white")
    table.add_column("Executor", style="magenta")

    for cap in capabilities:
        table.add_row(cap.name, cap.version, cap.category, cap.description, cap.execution.executor)

    console.print(table)
    console.print(f"\n[bold green]{len(capabilities)}[/] capabilities registered")


@app.command()
def inspect(name: str = typer.Argument(..., help="Capability name")):
    """Inspect a capability in detail."""
    from worthdoing_capabilities import CapabilityRuntime
    runtime = CapabilityRuntime()

    try:
        details = runtime.inspect(name)
    except KeyError as e:
        console.print(f"[red bold]Error:[/] {e}")
        raise typer.Exit(1)

    console.print(Panel(f"[bold cyan]{name}[/] v{details['version']}", title="Capability Details"))

    syntax = Syntax(json.dumps(details, indent=2, default=str), "json", theme="monokai")
    console.print(syntax)


@app.command()
def run(
    name: str = typer.Argument(..., help="Capability name"),
    input_json: str = typer.Option("{}", "--input", "-i", help="Input data as JSON string"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache"),
):
    """Execute a capability."""
    from worthdoing_capabilities import CapabilityRuntime
    runtime = CapabilityRuntime()

    try:
        input_data = json.loads(input_json)
    except json.JSONDecodeError as e:
        console.print(f"[red bold]Invalid JSON input:[/] {e}")
        raise typer.Exit(1)

    console.print(f"[bold]Running[/] [cyan]{name}[/]...")

    try:
        result = runtime.run(name, input_data, bypass_cache=no_cache)
        console.print(Panel("[bold green]Success[/]", title="Result"))
        syntax = Syntax(json.dumps(result, indent=2, default=str), "json", theme="monokai")
        console.print(syntax)
    except Exception as e:
        console.print(f"[red bold]Execution failed:[/] {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    path: str = typer.Argument(..., help="Path to capability.yaml"),
):
    """Validate a capability contract file."""
    from worthdoing_capabilities.contracts.loader import load_contract
    from worthdoing_capabilities.validation.validator import validate_contract

    filepath = Path(path)
    if not filepath.exists():
        console.print(f"[red bold]File not found:[/] {path}")
        raise typer.Exit(1)

    try:
        contract = load_contract(filepath)
        warnings = validate_contract(contract)

        console.print(f"[bold green]Valid:[/] {contract.name} v{contract.version}")

        if warnings:
            for w in warnings:
                console.print(f"  [yellow]Warning:[/] {w}")
        else:
            console.print("  [green]No warnings[/]")
    except Exception as e:
        console.print(f"[red bold]Validation failed:[/] {e}")
        raise typer.Exit(1)


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of records"),
    capability: str = typer.Option(None, "--capability", "-c", help="Filter by capability name"),
):
    """Show execution history."""
    from worthdoing_capabilities import CapabilityRuntime
    runtime = CapabilityRuntime()

    records = runtime.log.query(capability_name=capability, limit=limit)

    if not records:
        console.print("[dim]No execution records found[/]")
        return

    table = Table(title="Execution History", show_lines=True)
    table.add_column("Capability", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Duration", style="yellow")
    table.add_column("Cache", style="magenta")
    table.add_column("Timestamp", style="dim")

    for r in records:
        status_style = {"success": "green", "error": "red", "timeout": "yellow", "cache_hit": "blue"}.get(r.status, "white")
        table.add_row(
            r.capability_name,
            f"[{status_style}]{r.status}[/{status_style}]",
            f"{r.duration_ms:.1f}ms",
            r.cache_status,
            r.timestamp.strftime("%H:%M:%S"),
        )

    console.print(table)


if __name__ == "__main__":
    app()
