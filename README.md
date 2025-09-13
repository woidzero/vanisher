# Vanisher

[![PyPI - Version](https://img.shields.io/pypi/v/vanisher.svg)](https://pypi.org/project/vanisher)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vanisher)](https://pypi.org/project/vanisher)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vanisher.svg)](https://pypi.org/project/vanisher)

🔩 A flexible configuration management library for Python with dot notation support, environment variable overrides and more.

## Features

- JSON configuration file support
- Dot notation for accessing nested values
- Environment variable overrides
- Type-safe getters
- Dictionary-like interface
- Import/export to JSON, YAML, and TOML
- Deep merging of configurations
- Easy configuration updates and persistence
- Easy to use for both pros and beginners

## Installation

```bash
pip install vanisher
```

## Quick Start

```python
import vanisher

config = vanisher.Vanisher("config.json")

config.set({
    "server.port": 8080,
    "debug": False,
    "database.user.name": "user"
})

config.get("server.port") # prints: 8080
```

## Environment Variables

Environment variables automatically override config values when `env_override=True` (default).
Keys are converted to UPPERCASE with underscores: `database.host` → `DATABASE_HOST`

## Type-Safe Getters

```python
config.get_int("port", 8080)    # Returns int
config.get_bool("debug", False) # Returns bool
config.get_list("allowed_ips")  # Returns list
config.get_dict("settings")     # Returns dict
```

## Advanced Features

```python
# List all config keys
keys = config.list_keys()

# Export config
json_str = config.export("json")
yaml_str = config.export("yaml")  # Requires PyYAML
toml_str = config.export("toml")  # Requires toml

# Import config
config.import_('{"key": "value"}')
config.import_({"key": "value"})

# Merge configurations
config.merge({"new": "data"})
```

## License

`vanisher` is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
