"""Command-line interface."""

import asyncio

import typer

from app.io.cli.commands import create_security_command, update_candles_command

app = typer.Typer()


@app.command()
def create_security(ticker: str, board: str):
    """Create Security."""
    asyncio.run(create_security_command(ticker=ticker, board=board))
    pass


@app.command()
def update_candles():
    """Update Candles."""
    asyncio.run(update_candles_command())


app()
