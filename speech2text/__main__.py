"""
Allows the package to be run as a script.

Enables execution via `python -m speech2text ...`
"""

from .cli import cli

if __name__ == "__main__":
    cli()