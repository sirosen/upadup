import json
import urllib.request


def normalize_package_name(name: str):
    return name.lower().replace("_", "-")


def get_pkg_latest(name: str) -> str:
    with urllib.request.urlopen(
        f"https://pypi.python.org/pypi/{name}/json", timeout=30
    ) as conn:
        version_data = json.load(conn)
    return str(version_data["info"]["version"])
