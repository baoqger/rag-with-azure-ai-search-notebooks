"""Utility for rendering search results as rich tables."""

from typing import Any

from rich.console import Console
from rich.table import Table


def render_product_results(results: list[dict[str, Any]], title: str, show_reranker: bool = False) -> None:
    """Render product search results as a rich table.

    Args:
        results: List of search result documents
        title: Title for the table
        show_reranker: Whether to show reranker score column
    """
    console = Console()
    table = Table(title=title, show_lines=True)

    table.add_column("Score", justify="right", style="cyan", width=8)
    if show_reranker:
        table.add_column("Reranker", justify="right", style="red", width=8)
    table.add_column("Name", style="magenta", width=25)
    table.add_column("Description", style="white", width=50)
    table.add_column("Categories", style="blue", width=20)
    table.add_column("Price", justify="right", style="yellow", width=8)
    table.add_column("SKU", style="green", width=12)

    for doc in list(results):
        row = [
            f"{doc['@search.score']:.3f}",
        ]
        if show_reranker:
            row.append(f"{doc['@search.reranker_score']:.3f}")
        row.extend([
            doc["name"],
            doc["description"][:80] + "..." if len(doc["description"]) > 80 else doc["description"],
            ", ".join(doc["categories"]),
            f"${doc['price']:.2f}",
            doc["sku"],
        ])
        table.add_row(*row)

    console.print(table)
