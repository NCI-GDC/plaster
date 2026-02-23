import os
import uuid
from logging.config import dictConfig
from typing import Final, Literal, Optional, TypedDict, Union, cast

import toml
import yaml

DEFAULT_SETTINGS_FILE: Final[str] = "plaster.toml"


class LoggingConfig(TypedDict):
    level: str
    log_file: str


class EnvironmentVars(TypedDict, total=False):
    git_home: str


class Profile(TypedDict):
    url: str
    path: str
    type: Literal["local", "remote"]
    version: str
    is_git_tag: bool
    overwrite: bool
    local_directory: str
    namespace: str


class Config(TypedDict):
    title: str
    profiles: dict[str, Profile]
    environment: EnvironmentVars
    logging: LoggingConfig


class PlasterConfig:
    def __init__(self, cfg: Config) -> None:
        self.load_id = str(uuid.uuid4())
        self.cfg = cfg

    @property
    def title(self) -> str:
        return self.cfg["title"]

    @property
    def environment(self) -> EnvironmentVars:
        return self.cfg.get("environment", {})

    @property
    def logging(self) -> LoggingConfig:
        return self.cfg["logging"]

    def _configure_logger(self) -> None:
        cfg = self.logging

        level = cfg["level"]
        log_file = cfg["log_file"]
        lcfg = yaml.safe_load(
            f"""
            version: 1
            formatters:
              simple:
                format: '%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s'
            handlers:
              console:
                class: logging.StreamHandler
                level: {level}
                formatter: simple
                stream: ext://sys.stdout
              file:
                class: logging.handlers.RotatingFileHandler
                level: {level}
                formatter: simple
                filename: {log_file}
                maxBytes: 409600000
                backupCount: 10
            loggers:
              plaster:
                level: {level}
                handlers: [console, file]
                propagate: no
            root:
              level: {level}
              handlers: [console, file]
        """
        )

        dictConfig(lcfg)

    def _configure_env(self) -> None:
        for key, val in self.environment.items():
            os.environ[f"PLASTER_{key.upper()}"] = str(val)

    def configure(self) -> None:
        self._configure_env()
        self._configure_logger()

    def get_profile(self, name: str) -> Optional[Profile]:
        return self.cfg.get("profiles", {}).get(name)


def load_config(
    file_name: Union[os.PathLike, str] = DEFAULT_SETTINGS_FILE,
) -> PlasterConfig:
    with open(file_name) as f:
        raw_cfg = toml.load(f)
        cfg = PlasterConfig(cfg=cast(Config, raw_cfg))
        cfg.configure()

        return cfg
