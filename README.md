# Vanisher

[![PyPI - Version](https://img.shields.io/pypi/v/wvanisher.svg)](https://pypi.org/project/wvanisher)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/wvanisher)](https://pypi.org/project/wvanisher)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wvanisher.svg)](https://pypi.org/project/wvanisher)

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
pip install wvanisher
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

port = config.get("server.port")

print(port) # prints: 8080
```

## Environment Variables

Environment variables automatically override config values when `env_override=True` (default).
Keys are converted to UPPERCASE with underscores: `database.host` → `DATABASE_HOST`

```env
SERVER_PORT=8080
```

```python
import vanisher

config = vanisher.Vanisher("config.json", env_overrides=True)
port = config.get("server.port")

print(port) # prints: 8080
```

## Type-Safe Getters

```python
config.get_int("port", 8080)    # returns int
config.get_bool("debug", False) # returns bool
config.get_list("allowed_ips")  # returns list
config.get_dict("settings")     # returns dict
```

## Advanced Features

```python
# list all config keys
keys = config.list_keys()

# export config
json_str = config.export("json")
yaml_str = config.export("yaml")  # requires PyYAML
toml_str = config.export("toml")  # requires toml

# import config
config.import_('{"key": "value"}')
config.import_({"key": "value"})

# merge configurations
config.merge({"new": "data"})
```

## License

`vanisher` is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
