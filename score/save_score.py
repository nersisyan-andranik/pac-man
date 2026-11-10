import json
from typing import Any

from errors import ConfigError
from pathlib import Path


def _is_valid_entry(item: Any) -> bool:
    """Return True if item is a dict with a non-negative integer score."""
    if not isinstance(item, dict):
        return False
    score = item.get("score")
    return (
        isinstance(score, int)
        and not isinstance(score, bool)
        and score >= 0
    )


def _read_scores(path: str | Path) -> list[dict[str, Any]]:
    """Return all valid score entries ([] if file is missing or broken)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ConfigError("top-level JSON value must be a list")
    except FileNotFoundError:
        return []
    except (
        OSError, UnicodeError, json.JSONDecodeError, ConfigError
    ) as error:
        print(error)
        return []

    return [item for item in data if _is_valid_entry(item)]


def save_score(path: str | Path, player_name: str, score: int) -> bool:
    """Save a score, keeping one entry per player name.

    If the name already exists, the entry is updated only when the new
    score is higher. Names are compared without case ("Ann" == "ann").

    Args:
        path: Path to the highscore JSON file.
        player_name: Name entered by the player.
        score: Score to save.

    Returns:
        True if the file was changed, False if nothing was saved.
    """
    scores = _read_scores(path)
    key = player_name.casefold()

    for item in scores:
        if str(item.get("name", "")).casefold() == key:
            if score <= item["score"]:
                return False
            item["score"] = score
            break
    else:
        scores.append({"name": player_name, "score": score})

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError as error:
        print(error)
        return False
    return True
