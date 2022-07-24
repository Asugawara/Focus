import argparse
import hashlib
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from focus import Focus, parse_time

TEST_BACKUPED_CONTENTS = ["test", "contents", "backuped"]
TEST_BASENAME = "hosts"
TEST_CONTENTS = ["test", "contents"]
TEST_TARGET_DOMAINS = ["youtube.com", "instagram.com"]


class TestFocus(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_target_file = os.path.join(self.temp_dir, TEST_BASENAME)
        with open(self.temp_target_file, "w") as f:
            print("\n".join(TEST_CONTENTS), file=f)
        self.patcher = patch("focus.Focus.TARGET_FILE_PATH", self.temp_target_file)
        self.patcher.start()
        self.quiet = True

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.temp_dir)

    def test_focus_read(self):
        read_contents = Focus._read(self.temp_target_file)
        self.assertEqual(read_contents, TEST_CONTENTS)

    def test_focus_write(self):
        temp_file = os.path.join(self.temp_dir, "test_write.txt")
        Focus._write(temp_file, TEST_CONTENTS)
        with open(temp_file, "r") as f:
            wrote_contents = [line.strip() for line in f.readlines()]
        self.assertEqual(wrote_contents, TEST_CONTENTS)

    def test_focus_backup(self):
        focus = Focus(self.temp_dir, self.quiet)
        focus._backup()
        with open(focus.current_backup_path, "r") as backup_file:
            backup_contents = [line.strip() for line in backup_file.readlines()]
        self.assertEqual(backup_contents, TEST_CONTENTS)

    def test_focus_forbid_domains(self):
        focus = Focus(self.temp_dir, self.quiet)
        focus.forbid_domains(TEST_TARGET_DOMAINS)
        with open(self.temp_target_file, "r") as target_file:
            updated_contents = [line.strip() for line in target_file.readlines()]

        expected_contents = TEST_CONTENTS
        expected_contents += [focus.FOCUS_BOS]
        expected_contents += [
            f"{focus.DEFAULT_DST_IP} {t}" for t in TEST_TARGET_DOMAINS
        ]
        expected_contents += [focus.FOCUS_EOS]

        self.assertEqual(updated_contents, expected_contents)

    def test_focus_restore(self):
        byte_contents = bytes("".join(TEST_BACKUPED_CONTENTS), encoding="utf-8")
        backup_hash = hashlib.sha256(byte_contents).hexdigest()
        temp_backuped_file = os.path.join(self.temp_dir, backup_hash)
        with open(temp_backuped_file, "w") as backup_f:
            print("\n".join(TEST_BACKUPED_CONTENTS), file=backup_f)
        focus = Focus(self.temp_dir, self.quiet)
        focus.restore(backup_hash)
        with open(self.temp_target_file, "r") as f:
            restored_contents = [line.strip() for line in f.readlines()]
        self.assertEqual(restored_contents, TEST_BACKUPED_CONTENTS)

    def test_parse_time(self):
        self.assertEqual(parse_time("2d"), 2 * 86400)
        self.assertEqual(parse_time("3h"), 3 * 3600)
        self.assertEqual(parse_time("4m"), 4 * 60)
        self.assertEqual(parse_time("5s"), 5)

        with self.assertRaises(argparse.ArgumentTypeError):
            parse_time("6dm")
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_time("7.8s")


if __name__ == "__main__":
    unittest.main()
