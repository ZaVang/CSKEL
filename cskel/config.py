import tomli
from pathlib import Path
from typing import Dict, Any, List
import pathspec

DEFAULT_CONFIG = {
    "min_level": 1,
    "preserve_imports": True,
    "include_private": False,
    "smart_calls": True,
    "max_call_depth": 2,
}

class Config:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.cskel_toml_path = self.base_dir / "cskel.toml"
        self.skelignore_path = self.base_dir / ".skelignore"
        
        self.settings = self._load_config()
        self.ignore_spec = self._load_ignore_spec()

    def _load_config(self) -> Dict[str, Any]:
        config = DEFAULT_CONFIG.copy()
        if self.cskel_toml_path.is_file():
            with self.cskel_toml_path.open("rb") as f:
                try:
                    user_config = tomli.load(f)
                    if "cskel" in user_config:
                        config.update(user_config["cskel"])
                except tomli.TOMLDecodeError:
                    # Handle potential error gracefully
                    pass
        return config

    def _load_ignore_spec(self) -> pathspec.PathSpec:
        patterns: List[str] = []
        if self.skelignore_path.is_file():
            with self.skelignore_path.open("r", encoding="utf-8") as f:
                patterns = f.read().splitlines()
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def should_ignore(self, file_path: Path) -> bool:
        relative_path = file_path.relative_to(self.base_dir)
        return self.ignore_spec.match_file(str(relative_path))
