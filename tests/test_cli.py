"""Offline regression tests for the module command-line entry point."""

import subprocess
import sys
import unittest


class ModuleCLITest(unittest.TestCase):
    def run_module(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "epm", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_help(self):
        result = self.run_module("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Syntax: epm", result.stdout)

    def test_version(self):
        result = self.run_module("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip())

    def test_no_command_preserves_syntax_exit_code(self):
        result = self.run_module()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Syntax: epm", result.stderr)

    def test_invalid_command_preserves_error_exit_code(self):
        result = self.run_module("not-a-command")
        self.assertEqual(result.returncode, 9)
        self.assertIn("invalid command", result.stderr)


if __name__ == "__main__":
    unittest.main()
