#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
from typing import List


RELENG_DIR = Path(__file__).resolve().parent
ROOT_DIR = RELENG_DIR.parent


@dataclass
class FridaVersion:
    name: str
    major: int
    minor: int
    micro: int
    nano: int
    commit: str


def main(argv: List[str]):
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("repo", nargs="?", type=Path, default=ROOT_DIR)
        args = parser.parse_args()

        version = detect(args.repo)
        print(version.name)
    except Exception as e:
        print(f"Error in frida_version.py: {e}", file=sys.stderr)
        print("0.0.0")
        sys.exit(0)


def detect(repo: Path) -> FridaVersion:
    version_name = "0.0.0"
    major = 0
    minor = 0
    micro = 0
    nano = 0
    commit = ""

    if (repo / ".git").exists():
        description = subprocess.run(["git", "describe", "--tags", "--always", "--long"],
                                     cwd=repo,
                                     capture_output=True,
                                     encoding="utf-8").stdout

        if description.startswith("v"):
            description = description[1:]

        tokens = description.strip().replace("-", ".").split(".")
        if len(tokens) > 1:
            (raw_major, raw_minor, raw_micro, raw_nano, commit) = tokens[:3] + tokens[-2:]
            major = int(raw_major)
            minor = int(raw_minor)
            micro = int(raw_micro)
            try:
                nano = int(raw_nano)
            except ValueError:
                nano = 0
            
            if nano > 0:
                micro += 1

            if nano == 0:
                version_name = f"{major}.{minor}.{micro}"
            else:
                version_name = f"{major}.{minor}.{micro}-dev.{nano - 1}"
        else:
            commit = tokens[0]

    return FridaVersion(version_name, major, minor, micro, nano, commit)


if __name__ == "__main__":
    main(sys.argv)
