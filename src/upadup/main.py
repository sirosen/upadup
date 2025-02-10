from __future__ import annotations

import argparse
import sys

from .updater import UpadupUpdater


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="upadup -- the pre-commit additional_dependencies updater"
    )
    parser.add_argument(
        "--check",
        help="check and show diff, but do not update",
        action="store_true",
        default=False,
    )
    args = parser.parse_args(argv or sys.argv[1:])

    updater = UpadupUpdater()
    updater.run()

    if updater.has_updates():
        if args.check:
            print(updater.render_diff())
            sys.exit(1)
        else:
            print("apply updates...", end="")
            updater.apply_updates()
            print("done")
    else:
        print("no updates needed in any hook configs")
