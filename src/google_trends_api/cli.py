"""
CLI for Google Trends API.

Usage:
    gtrends trend --limit 5
    gtrends rel 아이폰 --limit 5
    gtrends cmp 삼성 애플
"""

import json

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ImportError:
    raise ImportError("CLI dependencies not installed. Run: pip install google-trends-api[cli]")

from . import trending, related, compare, interest

app = typer.Typer(help="Google Trends CLI - Fast trend data access")
console = Console()


@app.command()
def trend(
    geo: str = typer.Option("KR", "--geo", "-g", help="Country code"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results"),
    format: str = typer.Option("minimal", "--format", "-f", help="Output format: minimal, standard, full"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Get realtime trending keywords."""
    result = trending(geo=geo, limit=limit, format=format)

    if json_output:
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
    elif format == "minimal":
        for i, kw in enumerate(result, 1):
            console.print(f"{i}. {kw}")
    else:
        table = Table(title=f"Trending in {geo}")
        table.add_column("#", style="dim")
        table.add_column("Keyword", style="bold")
        table.add_column("Traffic")

        for i, item in enumerate(result, 1):
            table.add_row(str(i), item["keyword"], item.get("traffic", "N/A"))

        console.print(table)


@app.command()
def rel(
    keyword: str = typer.Argument(..., help="Keyword to find related queries"),
    geo: str = typer.Option("KR", "--geo", "-g", help="Country code"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Get related search queries for a keyword."""
    result = related(keyword=keyword, geo=geo, limit=limit)

    if json_output:
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        console.print(f"\n[bold]Related queries for '{keyword}':[/bold]")
        for i, kw in enumerate(result, 1):
            console.print(f"  {i}. {kw}")


@app.command()
def cmp(
    keywords: list[str] = typer.Argument(..., help="Keywords to compare"),
    geo: str = typer.Option("KR", "--geo", "-g", help="Country code"),
    days: int = typer.Option(90, "--days", "-d", help="Time period in days"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Compare keywords by average interest."""
    result = compare(keywords=keywords, geo=geo, days=days)

    if json_output:
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        table = Table(title=f"Keyword Comparison ({days} days)")
        table.add_column("Keyword", style="bold")
        table.add_column("Avg Interest", justify="right")

        sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
        for kw, score in sorted_result:
            table.add_row(kw, f"{score:.1f}")

        console.print(table)


@app.command()
def hist(
    keywords: list[str] = typer.Argument(..., help="Keywords to analyze"),
    geo: str = typer.Option("KR", "--geo", "-g", help="Country code"),
    days: int = typer.Option(7, "--days", "-d", help="Time period in days"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Get interest over time (history)."""
    result = interest(keywords=keywords, geo=geo, days=days)

    if json_output:
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        console.print(f"\n[bold]Interest over time ({days} days):[/bold]")
        console.print(f"Data points: {len(result.get('dates', []))}")
        for kw, values in result.get("values", {}).items():
            avg = sum(values) / len(values) if values else 0
            console.print(f"  {kw}: avg={avg:.1f}, min={min(values) if values else 0}, max={max(values) if values else 0}")


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
