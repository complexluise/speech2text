
import logging
from rich.logging import RichHandler

def setup_logging():
    """Set up a logger with RichHandler for pretty console output."""
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("rich")

log = setup_logging()
