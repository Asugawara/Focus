"""Focus is a simple CLI tool to edit /etc/hosts
`Focus` is a CLI tool to focus on your business by preventing you from viewing the website that breaks your concentration via `/etc/hosts`.
Good to use when you want to focus on a specific time.
It works well with Pomodoro.

    Usage example:
    focus = Forcus(backup_dir="backups")
    focus.forbid_domains(["instgram.com", "youtube.com"])

"""


from __future__ import annotations

import argparse
import hashlib
import os
import time
from typing import List, Optional

from logzero import logger  # type: ignore


class Focus:
    TARGET_FILE_PATH: str = "/etc/hosts"
    FOCUS_BOS: str = "# Added by Focus"
    FOCUS_EOS: str = "# End of Focus section"
    DEFAULT_DST_IP: str = "127.0.0.1"

    def __init__(self, backup_dir: str, quiet: bool = False) -> None:
        self.backup_dir: str = backup_dir
        self.quiet: bool = quiet
        self.hosts_contents: List[str] = self._read(self.TARGET_FILE_PATH)
        self._current_hash: str = ""
        self._current_backup_path: str = ""
        self._backup()

    def __enter__(self) -> Focus:
        return self

    def __exit__(self, *args) -> None:
        not self.quiet and logger.info(f"{self.TARGET_FILE_PATH} is restored")
        self.restore()

    @staticmethod
    def _read(path: str) -> List[str]:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        contents = []
        with open(path, "r") as f:
            for line in f.readlines():
                contents.append(line.strip())
        return contents

    @staticmethod
    def _write(path: str, contents: List[str]) -> None:
        with open(path, "w") as f:
            f.write("\n".join(contents))

    def _backup(self) -> None:
        os.makedirs(self.backup_dir, exist_ok=True)
        byte_contents = bytes("".join(self.hosts_contents), encoding="utf-8")
        self._current_hash = hashlib.sha256(byte_contents).hexdigest()
        self._current_backup_path = os.path.join(self.backup_dir, self._current_hash)
        if not os.path.exists(self._current_backup_path):
            self._write(self._current_backup_path, self.hosts_contents)
            not self.quiet and logger.info(
                f"Backup completed: {self._current_backup_path}"
            )

    def forbid_domains(self, domains: List[str]) -> None:
        if not self.hosts_contents:
            raise RuntimeError(f"Not Found {self.TARGET_FILE_PATH} contents")
        updated_contents = []
        is_focus_section = False
        for line in self.hosts_contents:
            if line.startswith(self.FOCUS_BOS):
                is_focus_section = True
                continue
            if is_focus_section and line.startswith(self.FOCUS_EOS):
                is_focus_section = False
                continue
            if not is_focus_section:
                updated_contents.append(line)
        updated_contents.append(self.FOCUS_BOS)
        for d in domains:
            updated_contents.append(f"{self.DEFAULT_DST_IP} {d}")
        updated_contents.append(self.FOCUS_EOS)
        self._write(self.TARGET_FILE_PATH, updated_contents)
        not self.quiet and logger.info(f"Target domains are forbidden: {domains}")

    def restore(self, hash: Optional[str] = None) -> None:
        if hash is None:
            hash = self._current_hash

        tgt_file = [
            backup for backup in os.listdir(self.backup_dir) if backup.startswith(hash)
        ]
        if len(tgt_file) != 1:
            raise RuntimeError(f"Backup file is not specified: {tgt_file}")
        backup_contents = self._read(os.path.join(self.backup_dir, tgt_file[0]))
        self._write(self.TARGET_FILE_PATH, backup_contents)

    @property
    def current_backup_path(self) -> str:
        return self._current_backup_path

    @property
    def current_backup_hash(self) -> str:
        return self._current_hash


SEC_IN_A_DAY: int = 86400
SEC_IN_A_HOUR: int = 3600
SEC_IN_A_MIN: int = 60


def parse_time(time_str: str) -> int:
    if not time_str[:-1].isdigit():
        raise argparse.ArgumentTypeError(f"Invalid syntax: {time_str}")

    sec = 0
    if time_str.endswith("d"):
        sec += int(time_str[:-1]) * SEC_IN_A_DAY
    elif time_str.endswith("h"):
        sec += int(time_str[:-1]) * SEC_IN_A_HOUR
    elif time_str.endswith("m"):
        sec += int(time_str[:-1]) * SEC_IN_A_MIN
    elif time_str.endswith("s"):
        sec += int(time_str[:-1])
    else:
        raise argparse.ArgumentTypeError(f"Invalid syntax: {time_str}")
    return sec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("domains", nargs="*", help="Domains to be forbidden")
    parser.add_argument(
        "-b",
        "--backup-dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "backups"),
        help="Directory where snapshots are stored",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t", "--time", type=parse_time, nargs="+", help="How long to forbid domains"
    )
    group.add_argument(
        "-n",
        "--never-ending",
        action="store_true",
        help="Never-ending to forbid the websites",
    )
    parser.add_argument("-r", "--restore", type=str, help="Restore /etc/hosts")
    parser.add_argument("-q", "--quiet", action="store_true", help="No output")
    args = parser.parse_args()

    if args.restore is not None:
        focus = Focus(args.backup_dir, args.quiet)
        focus.restore(args.restore)
        return

    if args.never_ending:
        focus = Focus(args.backup_dir, args.quiet)
        focus.forbid_domains(args.domains)
    else:
        with Focus(args.backup_dir, args.quiet) as focus:
            focus.forbid_domains(args.domains)
            if not args.quiet:
                for left in range(sum(args.time) * 100, 0, -1):
                    print(f"{left / 100:.2f} seconds left.", flush=True, end="\r")
                    time.sleep(1 / 100)
            else:
                time.sleep(sum(args.time))


if __name__ == "__main__":
    main()
