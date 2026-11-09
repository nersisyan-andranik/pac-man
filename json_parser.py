import json
import os,sys
from constants import EXPECTED_TYPES, DEFAULTS, REQUIRED_LEVEL_KEYS, LEVEL_EXPECTED_TYPES
from errors import ConfigError
from pathlib import Path


def _read_file(path: Path) -> str:
    """Read a configuration file using UTF-8 encoding.

    Args:
        path: Path to the configuration file.

    Returns:
        The complete contents of the file as a string.

    Raises:
        ConfigError: If the file does not exist, cannot be read,
            contains invalid UTF-8 text, or another I/O error occurs.
    """
    if not os.path.isfile(path):
        raise ConfigError(f"config file '{path}' not found")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError:
        raise ConfigError(f"cannot read '{path}' (permission denied)")
    except UnicodeDecodeError:
        raise ConfigError(f"'{path}' is not a valid text/UTF-8 file")
    except OSError as e:
        raise ConfigError(f"could not read '{path}' ({e})")


def _strip_comments(raw: str) -> str:
    """Remove supported comments from configuration text.

    Removes '#' and '//' line comments and '/* ... */' block
    comments while preserving comment-like characters inside
    double-quoted strings.

    Args:
        raw: Original configuration text.

    Returns:
        Configuration text with comments removed.

    Raises:
        ConfigError: If a block comment or a double-quoted string
            is not properly terminated.
    """
    result = []
    i = 0
    n = len(raw)
    in_string = False
    escape_next = False

    while i < n:
        c = raw[i]
        if in_string:
            result.append(c)
            if escape_next:
                escape_next = False
            elif c == "\\":
                escape_next = True
            elif c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            result.append(c)
            i += 1
            continue
        if c == "#":
            while i < n and raw[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and raw[i + 1] == "/":
            i += 2
            while i < n and raw[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and raw[i + 1] == "*":
            i += 2
            while i + 1 < n and not (raw[i] == "*" and raw[i + 1] == "/"):
                i += 1
            if i + 1 >= n:
                raise ConfigError("unterminated '/* ... */' comment in config file")
            i += 2
            continue
        result.append(c)
        i += 1
    if in_string:
        raise ConfigError("unterminated string literal in config file")
    return "".join(result)


def _parse_json(cleaned: str, path: Path) -> dict:
    """Parse cleaned JSON text into a dictionary.

    Args:
        cleaned: Configuration text after comment removal.
        path: Configuration file path, used in error messages.

    Returns:
        The parsed top-level JSON object as a dictionary.

    Raises:
        ConfigError: If the JSON is invalid or its top-level value
            is not a JSON object.
    """
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"invalid JSON in '{path}' (line {e.lineno}, column {e.colno}): {e.msg}"
        )

    if not isinstance(data, dict):
        raise ConfigError(
            f"'{path}' must contain a JSON object at the top level, "
            f"got {type(data).__name__}"
        )

    return data


def _apply_defaults(config: dict) -> dict:
    """Fill missing configuration keys with their default values.

    Existing values are preserved. Only keys absent from the
    configuration dictionary receive defaults.

    Args:
        config: Parsed configuration dictionary to update.

    Returns:
        The same dictionary, with missing default values added.
    """
    for key, default_value in DEFAULTS.items():
        if key not in config:
            config[key] = default_value
    return config


def _validate(config: dict) -> dict:
    """Validate configuration types, required keys, and values.

    Checks the expected types of top-level configuration values,
    ensures that at least one level exists, validates each level's
    required dimensions, and checks the supported positive or
    non-negative value constraints.

    Args:
        config: Configuration dictionary to validate.

    Returns:
        The same dictionary if all implemented checks pass.

    Raises:
        ConfigError: If a required key is missing, a value has an
            unexpected type, a level is invalid, or a checked
            value violates its constraints.
        KeyError: If an expected top-level key is missing before
            defaults have been applied.
    """
    for key, expected_type in EXPECTED_TYPES.items():
        value = config[key]
        if not isinstance(value, expected_type):
            expected_name = (
                expected_type.__name__
                if isinstance(expected_type, type)
                else " or ".join(t.__name__ for t in expected_type)
            )
            raise ConfigError(
                f"key '{key}' must be of type {expected_name}, "
                f"got {type(value).__name__}"
            )

    if not config["level"]:
        raise ConfigError("'level' must contain at least one level")

    for idx, level in enumerate(config["level"]):
        if not isinstance(level, dict):
            raise ConfigError(f"level #{idx} must be a JSON object")

        for key in REQUIRED_LEVEL_KEYS:
            if key not in level:
                raise ConfigError(f"level #{idx} is missing required key '{key}'")

        for key, expected_type in LEVEL_EXPECTED_TYPES.items():
            if key in level and not isinstance(level[key], expected_type):
                raise ConfigError(
                    f"level #{idx}: key '{key}' must be of type "
                    f"{expected_type.__name__}, got {type(level[key]).__name__}"
                )
            if key in level and level[key] <= 0:
                raise ConfigError(
                    f"level #{idx}: key '{key}' must be a positive number"
                )

    if config["lives"] <= 0:
        raise ConfigError("'lives' must be a positive integer")

    if config["pacgum"] < 0:
        raise ConfigError("'pacgum' must be zero or a positive integer")

    return config


def _config_path(arguments: list[str]) -> Path:
    """Resolve the required CLI config or the packaged default config."""
    if getattr(sys, "frozen", False) and len(arguments) == 1:
        bundle_root = Path(getattr(sys, "_MEIPASS", Path.cwd()))
        return bundle_root / "config.json"
    if len(arguments) != 2:
        raise ConfigError(f"Usage: {arguments[0]} <config.json>")
    path = Path(arguments[1]).expanduser()
    if path.suffix.lower() != ".json":
        raise ConfigError("configuration file must have a .json extension")
    return path.resolve()


def load_config() -> dict:
    """Load and validate a configuration file.

    Reads the file, removes supported comments, parses the remaining
    JSON, applies default values, and validates the resulting
    configuration.

    Args:
        path: Path to the configuration file.

    Returns:
        A validated configuration dictionary containing default
        values for keys that were missing from the file.

    Raises:
        ConfigError: If the file cannot be read, the JSON is invalid,
            required values are missing, or validation fails.
    """

    try:
        config_path = _config_path(sys.argv)
    except ConfigError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    try:
        raw = _read_file(config_path)
        cleaned = _strip_comments(raw)
        data = _parse_json(cleaned, config_path)
        data = _apply_defaults(data)
        data = _validate(data)
        return data
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)