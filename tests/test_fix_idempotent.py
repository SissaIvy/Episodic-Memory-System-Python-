import json
import os
import tempfile
import unittest

from episodic_memory.utils import load_system_from_path
from episodic_memory import MemoryStore
import memory_cli as cli


DATA_PATH = os.path.join(os.getcwd(), "EpisodicMemorySystem.json")


class TestFixIdempotent(unittest.TestCase):
    def test_fix_is_idempotent(self):
        # Run fix twice and compare outputs
        with tempfile.TemporaryDirectory() as td:
            out1 = os.path.join(td, "fixed1.json")
            out2 = os.path.join(td, "fixed2.json")

            args1 = cli.build_parser().parse_args(["fix", DATA_PATH, "--output", out1])
            ret1 = cli.cmd_fix(args1)
            self.assertEqual(ret1, 0)

            args2 = cli.build_parser().parse_args(["fix", out1, "--output", out2])
            ret2 = cli.cmd_fix(args2)
            self.assertEqual(ret2, 0)

            with open(out1, "r", encoding="utf-8") as f:
                d1 = json.load(f)
            with open(out2, "r", encoding="utf-8") as f:
                d2 = json.load(f)

            self.assertEqual(d1, d2)


if __name__ == "__main__":
    unittest.main()

