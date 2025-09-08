import json
import os
import shutil
import tempfile
import unittest

from episodic_memory import MemoryStore
from episodic_memory.utils import load_system_from_path


DATA_PATH = os.path.join(os.getcwd(), "EpisodicMemorySystem.json")


class TestMemoryStore(unittest.TestCase):
    def test_extract_last_json(self):
        data = load_system_from_path(DATA_PATH)
        self.assertIn("system_metadata", data)
        self.assertIn("memory_entries", data)

    def test_load_and_search(self):
        store = MemoryStore.load(DATA_PATH)
        # Lower threshold to ensure results for hash-embedding demo
        store.system.system_metadata.configuration.similarity_threshold = 0.1
        results = store.search("episodic memory system implementation", top_k=3)
        # Should at least try to retrieve the sample memory
        self.assertIsInstance(results, list)

    def test_add_and_save_roundtrip(self):
        # Work on a copy to avoid mutating the original file
        with tempfile.TemporaryDirectory() as td:
            tmp_path = os.path.join(td, "ems.json")
            data = load_system_from_path(DATA_PATH)
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            store = MemoryStore.load(tmp_path)
            before = store.system.system_metadata.total_memories
            store.system.system_metadata.configuration.similarity_threshold = 0.0
            mem_id = store.add_memory(
                raw_text="New memory for roundtrip test.",
                context_tags=["test"],
                importance_score=0.6,
                user_id="tester",
            )
            self.assertTrue(mem_id)
            store.save(tmp_path)

            # Reload and ensure count increased
            store2 = MemoryStore.load(tmp_path)
            after = store2.system.system_metadata.total_memories
            self.assertGreater(after, before)


if __name__ == "__main__":
    unittest.main()

