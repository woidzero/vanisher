import json
import os
from tempfile import NamedTemporaryFile
from typing import Any, Generator

import pytest

from vanisher import Vanisher


@pytest.fixture
def config_file() -> Generator[str, Any, None]:
    with NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
        tmp.write(json.dumps({"server": {"host": "localhost"}, "debug": False}))
        tmp_path = tmp.name
    yield tmp_path
    os.remove(tmp_path)


@pytest.fixture
def config(config_file) -> Vanisher:
    return Vanisher(config_file)


def test_get_set_has(config) -> None:
    config.set("server.port", 8080)
    assert config.get("server.host") == "localhost"
    assert config.get("server.port") == 8080
    assert config.has("server.host") is True
    assert config.has("server.notexist") is False

    config.set({"db.user": "admin", "db.pass": "secret"})
    assert config.get("db.user") == "admin"
    assert config.get("db.pass") == "secret"


def test_multi_get(config) -> None:
    config.set("server.port", 8080)
    config.set({"db.user": "admin"})
    multi = config.get("server.host", "server.port", "db.user")
    assert multi == {
        "server.host": "localhost",
        "server.port": 8080,
        "db.user": "admin",
    }


def test_delete(config) -> None:
    config.set({"db.pass": "secret"})
    deleted = config.delete("db.pass", _return=True)
    assert deleted == {"db.pass": "secret"}
    assert config.has("db.pass") is False


def test_type_safe_getters(config) -> None:
    config.set({"int_val": "123", "float_val": "3.14", "bool_val": "true", "list_val": "a,b,c"})
    assert config.get_int("int_val") == 123
    assert config.get_float("float_val") == 3.14
    assert config.get_bool("bool_val") is True
    assert config.get_str("int_val") == "123"
    assert config.get_list("list_val") == ["a", "b", "c"]

    config.set("nested.dict.key", "value")
    assert config.get_dict("nested.dict") == {"key": "value"}


def test_env_override(config, monkeypatch) -> None:
    config.set("server.port", 8080)

    monkeypatch.setenv("SERVER_PORT", "9090")
    monkeypatch.setenv("DEBUG", "true")

    assert config.get_int("server.port") == 9090  # overridden by env
    assert config.get_bool("debug") is True

    config.env_override = False
    assert config.get_int("server.port") == 8080
    config.env_override = True


def test_dict_style_access(config) -> None:
    config["dict_style.key"] = "ds_value"
    assert config["dict_style.key"] == "ds_value"
    del config["dict_style.key"]
    assert "dict_style.key" not in config


def test_list_keys(config) -> None:
    keys = config.list_keys()
    assert isinstance(keys, list)
    assert "server.host" in keys


def test_merge(config) -> None:
    config.merge({"merge_test": {"a": 1, "b": 2}})
    assert config.get("merge_test.a") == 1


def test_reload(config) -> None:
    config.set("temp_key", "temp")
    config.reload()
    assert config.get("temp_key") == "temp"


def test_clear(config) -> None:
    config.set("temp_key", "temp")
    config.clear()
    assert len(config) == 0


def test_import_export(config) -> None:
    config.import_({"imported": {"x": 1, "y": 2}})
    exported = config.export()
    exported_dict = json.loads(exported)
    assert exported_dict["imported"]["x"] == 1
