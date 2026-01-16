"""
Configuration management for user preferences.
Saves and loads settings between application sessions.
"""

import json
from pathlib import Path
from typing import Any, Optional


class Config:
    """
    Manages application configuration and user preferences.
    Stores settings in a JSON file in the user's home directory.
    """

    DEFAULT_CONFIG = {
        "last_source_directory": "",
        "last_output_directory": "",
        "last_icon_type": "square",
        "window_geometry": "480x680"
    }

    def __init__(self, app_name: str = "msstoreicons"):
        """
        Initialize configuration manager.

        Args:
            app_name: Name of the application (used for config directory)
        """
        self.app_name = app_name
        self.config_dir = Path.home() / f".{app_name}"
        self.config_file = self.config_dir / "config.json"
        self.config = self.DEFAULT_CONFIG.copy()

        # Load existing config if available
        self.load()

    def load(self) -> None:
        """Load configuration from file. Creates default if doesn't exist."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults (in case new keys were added)
                    self.config = {**self.DEFAULT_CONFIG, **loaded_config}
            else:
                # Create config directory if it doesn't exist
                self.config_dir.mkdir(parents=True, exist_ok=True)
                # Save default config
                self.save()
        except Exception as e:
            # If loading fails, use defaults
            print(f"Warning: Could not load config: {e}")
            self.config = self.DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Write config file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save to file.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save()

    def get_last_source_directory(self) -> str:
        """Get the last used source image directory."""
        return self.get("last_source_directory", "")

    def set_last_source_directory(self, directory: str) -> None:
        """Save the last used source image directory."""
        self.set("last_source_directory", directory)

    def get_last_output_directory(self) -> str:
        """Get the last used output directory."""
        return self.get("last_output_directory", "")

    def set_last_output_directory(self, directory: str) -> None:
        """Save the last used output directory."""
        self.set("last_output_directory", directory)

    def get_last_icon_type(self) -> str:
        """Get the last selected icon type."""
        return self.get("last_icon_type", "square")

    def set_last_icon_type(self, icon_type: str) -> None:
        """Save the last selected icon type."""
        self.set("last_icon_type", icon_type)

    def get_window_geometry(self) -> str:
        """Get the last window geometry."""
        return self.get("window_geometry", "480x550")

    def set_window_geometry(self, geometry: str) -> None:
        """Save the window geometry."""
        self.set("window_geometry", geometry)

    def clear(self) -> None:
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
