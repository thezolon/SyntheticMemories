"""
CLI interface for Memory Agent using Typer
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .memory_manager import MemoryManager

app = typer.Typer(
    name="memory",
    help="Privacy-first local cognitive memory agent",
    add_completion=False,
)

console = Console()

# Global manager instance (lazy-loaded)
_manager = None


def get_manager() -> MemoryManager:
    """Get or create memory manager"""
    global _manager
    if _manager is None:
        try:
            _manager = MemoryManager()
        except Exception as e:
            console.print(f"[red]Error initializing Memory Agent: {e}[/red]")
            console.print("\nHave you run setup? Try: [cyan]memory setup[/cyan]")
            raise typer.Exit(1)
    return _manager


@app.command()
def add(
    text: str = typer.Argument(None, help="Memory text to store"),
    tag: list[str] = typer.Option([], "--tag", "-t", help="Tags for the memory"),
    file: typer.FileText = typer.Option(None, "--file", "-f", help="Read from file"),
):
    """Add a new memory"""
    if file:
        text = file.read()
    elif not text:
        console.print("[red]Error: Provide text or use --file[/red]")
        raise typer.Exit(1)

    manager = get_manager()

    with console.status("[bold cyan]Adding memory..."):
        memory = manager.add_memory(text, tags=list(tag))

    console.print(f"[green]✓[/green] Memory saved (id: [cyan]{memory.id}[/cyan])")
    console.print(f"Content: {text[:100]}{'...' if len(text) > 100 else ''}")
    if tag:
        console.print(f"Tags: {', '.join(tag)}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, "--limit", "-n", help="Number of results"),
):
    """Search memories semantically"""
    manager = get_manager()

    console.print(f"Searching for: [cyan]{query}[/cyan]\n")

    with console.status("[bold cyan]Searching..."):
        results = manager.search(query, limit=limit)

    if not results:
        console.print("[yellow]No memories found[/yellow]")
        return

    console.print(f"Found {len(results)} result(s):\n")

    for i, result in enumerate(results, 1):
        score_percent = int(result.score * 100)
        content = result.memory.content[:200]
        if len(result.memory.content) > 200:
            content += "..."

        console.print(
            Panel(
                f"{content}\n\n"
                f"📅 {result.memory.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                f"🏷️  {', '.join(result.memory.tags) if result.memory.tags else 'no tags'}",
                title=f"[{i}] {result.memory.id} (similarity: {score_percent}%)",
                border_style="cyan",
            )
        )


@app.command()
def show(memory_id: str = typer.Argument(..., help="Memory ID")):
    """Show full memory details"""
    manager = get_manager()
    memory = manager.get_memory(memory_id)

    if not memory:
        console.print(f"[red]Memory {memory_id} not found[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold]Content:[/bold]\n{memory.content}\n\n"
            f"[bold]Created:[/bold] {memory.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold]Tags:[/bold] {', '.join(memory.tags) if memory.tags else 'none'}",
            title=f"Memory: {memory.id}",
            border_style="green",
        )
    )


@app.command()
def ask(question: str = typer.Argument(..., help="Question to ask")):
    """Ask a question using LLM"""
    manager = get_manager()

    console.print(f"Question: [cyan]{question}[/cyan]\n")

    with console.status("[bold cyan]Thinking..."):
        try:
            result = manager.ask(question)
        except Exception as e:
            console.print(f"[yellow]LLM not configured: {e}[/yellow]")
            console.print("\nFalling back to search results only...")
            results = manager.search(question, limit=3)
            if results:
                console.print("\nRelevant memories:")
                for r in results:
                    console.print(f"• {r.memory.content[:150]}...")
            raise typer.Exit(0)

    console.print(Panel(result.answer, title="Answer", border_style="green"))

    if result.sources:
        console.print(f"\n[dim]Sources: {', '.join(result.sources)}[/dim]")


@app.command()
def list(
    tag: str = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of memories"),
):
    """List recent memories"""
    console.print("[yellow]List command not yet fully implemented[/yellow]")
    console.print("Use [cyan]search[/cyan] instead for now")


@app.command()
def delete(memory_id: str = typer.Argument(..., help="Memory ID")):
    """Delete a memory"""
    manager = get_manager()

    # Check if exists
    memory = manager.get_memory(memory_id)
    if not memory:
        console.print(f"[red]Memory {memory_id} not found[/red]")
        raise typer.Exit(1)

    # Show what will be deleted
    console.print(f"Content: {memory.content[:100]}...")

    if typer.confirm(f"\nDelete memory {memory_id}?"):
        manager.delete_memory(memory_id)
        console.print(f"[red]✓[/red] Memory {memory_id} deleted")
    else:
        console.print("Cancelled")


@app.command()
def stats():
    """Show memory statistics"""
    manager = get_manager()

    stats = manager.get_stats()

    table = Table(title="Memory Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Memories", str(stats["total_memories"]))
    table.add_row("Storage Used", stats.get("storage_used", "N/A"))
    table.add_row("Average Query Time", stats.get("avg_query_time", "N/A"))

    console.print(table)


@app.command()
def setup():
    """Initial setup and configuration"""
    from pathlib import Path

    from .config import Config

    console.print("[bold cyan]Memory Agent Setup[/bold cyan]\n")

    # Check if already set up
    config_path = Path.home() / ".memory-agent" / "config.yaml"
    if config_path.exists():
        console.print("[yellow]Already configured. Delete ~/.memory-agent to start fresh.[/yellow]")
        return

    # Create directories
    base_dir = Path.home() / ".memory-agent"
    for d in ["data/vectors", "models/embeddings", "models/llm", "logs"]:
        (base_dir / d).mkdir(parents=True, exist_ok=True)

    console.print("[green]✓[/green] Created directories")

    # Save default config
    config = Config()
    config.save()
    console.print("[green]✓[/green] Created configuration")

    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("\nNext steps:")
    console.print(
        "1. [optional] Download LLM model for Q&A: [cyan]python scripts/download_models.py[/cyan]"
    )
    console.print("2. Add your first memory: [cyan]memory add 'Your first memory'[/cyan]")
    console.print("3. Search: [cyan]memory search 'query'[/cyan]")


if __name__ == "__main__":
    app()
