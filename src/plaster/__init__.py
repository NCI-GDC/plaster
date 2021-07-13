from pkg_resources import get_distribution

from plaster.config import load_config

VERSION = get_distribution(__name__).version
