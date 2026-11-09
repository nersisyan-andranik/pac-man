import json
from errors import ConfigError


def _read_scores(path: str) -> list[dict]:
    """Return all valid score entries from the file ([] if missing or broken)."""
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

    return [
        item for item in data
        if isinstance(item, dict) and isinstance(item.get("score"), (int, float))
    ]


def save_score(path: str, player_name: str, score: int) -> bool:
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