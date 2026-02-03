"""
Test CLI interface
"""

from typer.testing import CliRunner

from memory_agent.cli import app

runner = CliRunner()


def test_add_command():
    """Test add command"""
    result = runner.invoke(app, ["add", "Test memory content"])
    assert result.exit_code == 0
    assert "Memory saved" in result.stdout


def test_search_command():
    """Test search command"""
    result = runner.invoke(app, ["search", "test query"])
    assert result.exit_code == 0


def test_stats_command():
    """Test stats command"""
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0
    assert "Memory Statistics" in result.stdout


def test_setup_command():
    """Test setup command"""
    result = runner.invoke(app, ["setup"])
    assert result.exit_code == 0
