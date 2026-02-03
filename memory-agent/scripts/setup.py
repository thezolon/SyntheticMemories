#!/usr/bin/env python3
"""
Initial setup wizard for Memory Agent
"""

from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def create_directories():
    """Create necessary directories"""
    base_dir = Path.home() / ".memory-agent"
    dirs = [
        base_dir / "data" / "vectors",
        base_dir / "models" / "embeddings",
        base_dir / "models" / "llm",
        base_dir / "logs",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        console.print(f"✓ Created: {d}")


def setup_config():
    """Interactive configuration setup"""
    from memory_agent.config import Config
    
    console.print("\n[bold]Configuration Setup[/bold]\n")
    
    config = Config()
    
    # Ask about GPU
    use_gpu = Confirm.ask("Do you have a GPU and want to use it?", default=False)
    if use_gpu:
        config.embedding.device = "cuda"
        config.llm.n_gpu_layers = 35
    
    # Save config
    config.save()
    console.print("✓ Configuration saved")


def main():
    """Run setup wizard"""
    console.print("[bold cyan]Memory Agent Setup Wizard[/bold cyan]\n")
    
    try:
        # Create directories
        console.print("[bold]Step 1: Creating directories[/bold]")
        create_directories()
        
        # Setup config
        console.print("\n[bold]Step 2: Configuration[/bold]")
        setup_config()
        
        # Instructions
        console.print("\n[bold green]✓ Setup complete![/bold green]\n")
        console.print("Next steps:")
        console.print("1. Download models: python scripts/download_models.py")
        console.print("2. Add your first memory: memory add 'Your first memory'")
        console.print("3. Search: memory search 'query'")
        console.print("\nFor help: memory --help")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Setup failed: {e}[/bold red]")


if __name__ == "__main__":
    main()
