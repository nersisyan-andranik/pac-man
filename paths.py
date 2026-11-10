from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print(BASE_DIR)


def asset_path(relative_path: str) -> str:
    """Return the absolute path to a game asset.

    Args:
        relative_path: Path relative to the assets directory.

    Returns:
        Absolute path to the requested asset.
    """
    return str(BASE_DIR / "assets" / relative_path)
