"""Entry point for the notes command."""

import sqlite3
from pathlib import Path

import click

DB_PATH = Path.home() / ".notes" / "notes.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL)")
    return conn


@click.group()
def cli() -> None:
    """Command-line notebook."""


@cli.command()
@click.argument("body")
def add(body: str) -> None:
    with _connect() as conn:
        conn.execute("INSERT INTO notes (body) VALUES (?)", (body,))


@cli.command("list")
def list_notes() -> None:
    with _connect() as conn:
        for note_id, body in conn.execute("SELECT id, body FROM notes ORDER BY id"):
            click.echo(f"{note_id}: {body}")


@cli.command()
@click.argument("term")
def search(term: str) -> None:
    with _connect() as conn:
        rows = conn.execute("SELECT id, body FROM notes WHERE body LIKE ?", (f"%{term}%",))
        for note_id, body in rows:
            click.echo(f"{note_id}: {body}")
