import json
from errors import ConfigError
from pathlib import Path


def load_top_scores(path: str | Path, limit: int = 10) -> list[str]:
    """Load the best scores from a JSON file and format them for display.
    The file must contain a JSON list of objects, for example:
    [{"name": "AAA", "score": 1200}, {"name": "BBB", "score": 800}]

    Items that are not dicts, or that have no numeric "score", are ignored.
    The remaining items are sorted from the highest score to the lowest.
    Args:
        path: Path to the highscore JSON file.
        limit: Maximum number of scores to return (default: 10).
    Returns:
        A list of formatted lines such as "1. AAA - 1200 pts", ordered from
        the best score to the worst. The list is empty if the file is
        missing, unreadable, invalid, or contains no valid scores.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ConfigError("top-level JSON value must be a list")
    except FileNotFoundError:
        return []
    except (OSError, UnicodeError, json.JSONDecodeError, ConfigError) as error:
        print(error)
        return []

    valid = [
        item
        for item in data
        if (
                isinstance(item, dict)
                and isinstance(item.get("score"), (int, float))
        )
    ]
    best = sorted(valid, key=lambda item: item["score"], reverse=True)[:limit]

    return [
        f"{index}. {item.get('name', '')} - {item['score']} pts"
        for index, item in enumerate(best, start=1)
    ]
