"""
## Vanisher
~~~~~~~~
A flexible configuration management library for Python with dot notation support, environment variable overrides, and more.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

__all__ = ["Vanisher"]


class Vanisher:
    def __init__(self, path: str, env_override: bool = True) -> None:
        """
        Initialize Vanisher.

        Args:
            path (str): Path to JSON config file.
            env_override (bool): If True, environment variables override config values.
        """
        self._path = path
        self._file = os.path.basename(self._path)
        self._data = self._safe_read()
        self.env_override = env_override

    @property
    def path(self) -> str:
        return self._path

    @property
    def data(self) -> dict:
        return self._data

    @property
    def file(self) -> str:
        return self._file

    # -----------------------------
    # ENVIRONMENT OVERRIDE
    # -----------------------------
    def _env_key(self, key: str) -> str:
        """Convert dot-notation key to UPPERCASE_UNDERSCORE."""
        return key.replace(".", "_").upper()

    def _check_env(self, key: str, default: Any = None) -> Any:
        if not self.env_override:
            return None
        env_key = self._env_key(key)
        return os.getenv(env_key, default)

    # -----------------------------
    # CORE ACCESS
    # -----------------------------
    def _resolve(self, key: str, default: Any | None = None) -> Any:
        """Resolve a single key with env override and fallback to config data."""
        env_val = self._check_env(key)
        if env_val is not None:
            return env_val

        return self._get_single(key, default)

    def get(self, *keys: str, default: Any | None = None) -> Any:
        if len(keys) == 1:
            return self._resolve(keys[0], default)

        return {k: self._resolve(k, default) for k in keys}

    def _get_single(self, key: str, default: Any | None = None) -> Any:
        keys = key.split(".")
        current = self._data
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return default
            current = current[k]

        return current

    def has(self, key: str) -> bool:
        if self.env_override and self._check_env(key) is not None:
            return True

        keys = key.split(".")
        current = self._data
        for k in keys:
            if not isinstance(current, dict) or k not in current:
                return False

            current = current[k]

        return True

    def set(self, key: str | dict, value: Any = None) -> None:
        """Set single or multiple keys."""
        if isinstance(key, dict):
            for k, v in key.items():
                self._set_single(k, v)
        elif isinstance(key, str):
            self._set_single(key, value)
        else:
            msg = "Key must be str or dict"
            raise TypeError(msg)

        self.write(self._data)

    def _set_single(self, key: str, value: Any) -> None:
        keys = key.split(".")
        current = self._data
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    def delete(self, *keys: str, _return: bool = False) -> dict | None:
        """
        Delete one or more keys.

        Args:
            *keys: Dot-notation keys to delete.
            _return: If True, return deleted {key: value}.

        Returns:
            Optional[dict]: Deleted key-value pairs if _return=True
        """
        deleted = {}
        for key in keys:
            value = self._delete_single(key)
            if value is not None:
                deleted[key] = value
        self.write(self._data)
        return deleted if _return else None

    def _delete_single(self, key: str) -> Any | None:
        keys = key.split(".")
        current = self._data
        for k in keys[:-1]:
            if not isinstance(current, dict) or k not in current:
                return None
            current = current[k]
        if isinstance(current, dict) and keys[-1] in current:
            value = current[keys[-1]]
            del current[keys[-1]]
            return value
        return None

    # -----------------------------
    # TYPE-SAFE GETTERS
    # -----------------------------

    def get_int(self, key: str, default: bool | None = None) -> int | None:
        val = self._resolve(key, default)
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: bool | None = None) -> float | None:
        val = self._resolve(key, default)
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool | None = None) -> bool | None:
        val = self._resolve(key, default)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            val = val.strip().lower()
            if val in {"true", "yes", "1", "on"}:
                return True
            if val in {"false", "no", "0", "off"}:
                return False
        if isinstance(val, (int, float)):
            return bool(val)
        return default

    def get_str(self, key: str, default: str | None = None) -> str | None:
        val = self._resolve(key, default)
        return str(val) if val is not None else default

    def get_list(self, key: str, default: list | None = None) -> list | None:
        val = self._resolve(key, default)
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            return [v.strip() for v in val.split(",")]
        return default

    def get_dict(self, key: str, default: dict | None = None) -> dict | None:
        val = self._resolve(key, default)
        return val if isinstance(val, dict) else default

    # -----------------------------
    # EXTRA FEATURES
    # -----------------------------
    def list_keys(self) -> list[str]:
        result = []

        def _walk(d: dict, prefix="") -> None:
            for k, v in d.items():
                path = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    _walk(v, path)
                else:
                    result.append(path)

        _walk(self._data)
        return result

    def to_dict(self) -> dict:
        return deepcopy(self._data)

    def merge(self, new_data: dict) -> None:
        def _deep_merge(a, b) -> None:
            for k, v in b.items():
                if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                    _deep_merge(a[k], v)
                else:
                    a[k] = deepcopy(v)

        _deep_merge(self._data, new_data)
        self.write(self._data)

    def reload(self) -> None:
        self._data = self._safe_read()

    def clear(self, persist: bool = False) -> None:
        self._data.clear()
        if persist:
            self.write(self._data)

    def export(self, _format: str = "json") -> str:
        if _format == "json":
            return json.dumps(self._data, indent=4, ensure_ascii=False)

        if _format == "yaml":
            try:
                import yaml

                return yaml.dump(self._data)
            except ImportError:
                msg = "PyYAML not installed"
                raise RuntimeError(msg) from ImportError

        if _format == "toml":
            try:
                import toml

                return toml.dumps(self._data)
            except ImportError:
                msg = "toml not installed"
                raise RuntimeError(msg) from ImportError

        msg = "Unsupported format"
        raise ValueError(msg)

    def import_(self, data: dict | str, merge: bool = True) -> None:
        if isinstance(data, str):
            data = json.loads(data)
        if not isinstance(data, dict):
            msg = "import_() expects dict or JSON string"
            raise TypeError(msg)
        if merge:
            self.merge(data)
        else:
            self._data = deepcopy(data)
            self.write(self._data)

    # -----------------------------
    # MAGIC METHODS
    # -----------------------------
    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __len__(self) -> int:
        return len(self.list_keys())

    def __iter__(self):
        return iter(self.list_keys())

    def __repr__(self) -> str:
        return f"<Config file='{self._file}' keys={len(self)}>"

    # -----------------------------
    # FILE OPS
    # -----------------------------
    def update(self, data: dict | None = None) -> None:
        if data:
            self._data.update(data)
        self.write(self._data)

    def write(self, data: dict) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            msg = "Failed to write config file"
            raise RuntimeError(msg) from e

    def _safe_read(self) -> dict:
        if not os.path.isfile(self._path):
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({}, f)
                return {}
        try:
            with open(self._path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
