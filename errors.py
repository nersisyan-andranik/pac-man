class ConfigError(Exception):
    """Raised for any problem with loading or validating the config file."""


class MazeGenerationError(Exception):
    """Raised when maze generation fails or returns invalid data."""
