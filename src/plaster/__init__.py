from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("gdc-plaster")
except PackageNotFoundError:
    # package is not installed
    pass
