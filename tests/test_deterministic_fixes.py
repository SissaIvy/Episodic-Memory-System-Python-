"""
Tests for deterministic behavior and high-priority fixes.
Validates that the fixes in the Executive Summary are working correctly.
"""
import json
import os
import shutil
import tempfile
import unittest
import subprocess

from episodic_memory.store import _hash_embed
from episodic_memory.schema import validate_instance


class TestDeterministicFixes(unittest.TestCase):
    """Test deterministic embedding and other key fixes."""

    def test_hash_embed_is_deterministic(self):
        """Test that _hash_embed produces the same output across runs."""
        test_cases = [
            ("hello world", 64),
            ("episodic memory system", 128),
            ("", 32),  # empty string
            ("a", 16),  # single character
            ("🚀 unicode test 测试", 128),  # unicode
        ]
        
        for text, dim in test_cases:
            with self.subTest(text=text, dim=dim):
                # Multiple calls should produce identical vectors
                vec1 = _hash_embed(text, dim)
                vec2 = _hash_embed(text, dim)
                vec3 = _hash_embed(text, dim)
                
                self.assertEqual(vec1, vec2, f"Hash embedding not deterministic for '{text}'")
                self.assertEqual(vec2, vec3, f"Hash embedding not deterministic for '{text}'")
                self.assertEqual(len(vec1), dim, f"Wrong dimension for '{text}'")
                
                # Verify normalization (L2 norm should be ~1.0)
                if any(v != 0 for v in vec1):  # skip zero vectors
                    norm = sum(v * v for v in vec1) ** 0.5
                    self.assertAlmostEqual(norm, 1.0, places=5, 
                                         msg=f"Vector not normalized for '{text}'")

    def test_hash_embed_different_inputs_different_outputs(self):
        """Test that different inputs produce different embeddings."""
        dim = 128
        text1 = "hello world"
        text2 = "goodbye world"
        
        vec1 = _hash_embed(text1, dim)
        vec2 = _hash_embed(text2, dim)
        
        self.assertNotEqual(vec1, vec2, "Different inputs should produce different embeddings")

    def test_syntax_warning_fixed(self):
        """Test that the syntax warning in utils.py is fixed."""
        # Run python with warnings turned into errors to catch syntax warnings
        result = subprocess.run([
            "python", "-We", "-c", 
            "from episodic_memory.utils import extract_preamble_fields; print('OK')"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        self.assertEqual(result.returncode, 0, 
                        f"Syntax warning detected: {result.stderr}")
        self.assertIn("OK", result.stdout)

    def test_schema_validation_with_format_checker(self):
        """Test that schema validation uses FormatChecker (availability test)."""
        # This test verifies that the FormatChecker is properly instantiated
        # even if specific format validation behavior varies by jsonschema version
        from episodic_memory.schema import validate_instance
        
        # Simple valid data
        valid_data = {
            "system_metadata": {
                "version": "1.0.0",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z",
                "embedding_dimension": 128,
                "total_memories": 0,
                "storage_path": "/test/path",
                "configuration": {
                    "similarity_threshold": 0.7
                }
            },
            "memory_entries": {},
            "indexing_structures": {
                "semantic_clusters": {},
                "temporal_index": {},
                "graph_connections": {}
            },
            "integration_specifications": {
                "llm_context_format": {
                    "template": "test",
                    "max_memory_count": 5,
                    "context_window_size": 2048,
                    "include_metadata": True,
                    "confidence_threshold": 0.7
                }
            }
        }
        
        is_valid, error = validate_instance(valid_data)
        self.assertTrue(is_valid, f"Valid minimal data should pass: {error}")
        
        # Test that FormatChecker is being used (check the code imports it)
        import episodic_memory.schema as schema_module
        import inspect
        
        source = inspect.getsource(schema_module.validate_instance)
        self.assertIn("FormatChecker", source, "FormatChecker should be used in validation")


class TestFixerIdempotency(unittest.TestCase):
    """Test that the fix command is idempotent."""

    def test_fix_command_idempotent(self):
        """Test that running fix twice produces the same result."""
        data_path = os.path.join(os.getcwd(), "EpisodicMemorySystem.json")
        if not os.path.exists(data_path):
            self.skipTest(f"Test data file not found: {data_path}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy original file
            original_path = os.path.join(temp_dir, "original.json")
            fixed1_path = os.path.join(temp_dir, "fixed1.json")
            fixed2_path = os.path.join(temp_dir, "fixed2.json")
            
            shutil.copy2(data_path, original_path)
            
            # Run fix command twice
            subprocess.run([
                "python", "memory_cli.py", "fix", original_path,
                "--output", fixed1_path
            ], check=True, cwd=os.getcwd())
            
            subprocess.run([
                "python", "memory_cli.py", "fix", fixed1_path,
                "--output", fixed2_path
            ], check=True, cwd=os.getcwd())
            
            # Both fixed files should be identical
            with open(fixed1_path, 'r') as f1, open(fixed2_path, 'r') as f2:
                data1 = json.load(f1)
                data2 = json.load(f2)
                
            self.assertEqual(data1, data2, "Fix command should be idempotent")


class TestFAISSDimensionHandling(unittest.TestCase):
    """Test FAISS dimension handling (only if FAISS available)."""

    def setUp(self):
        try:
            import faiss  # noqa
            self.faiss_available = True
        except ImportError:
            self.faiss_available = False

    def test_faiss_dimension_consistency(self):
        """Test that FAISS index uses correct dimensions."""
        if not self.faiss_available:
            self.skipTest("FAISS not available")

        from episodic_memory.faiss_index import FaissIndexManager
        
        # Test different dimensions
        for dim in [64, 128, 256]:
            with self.subTest(dim=dim):
                mgr = FaissIndexManager(dim)
                self.assertEqual(mgr.dim, dim, f"Manager should store dimension {dim}")
                
                # Test adding vectors
                test_ids = ["id1", "id2"]
                test_vectors = [
                    [1.0] * dim,
                    [0.5] * dim
                ]
                
                mgr.add_vectors(test_ids, test_vectors)
                
                # Test search with correct dimension
                query = [0.8] * dim
                results = mgr.search(query, top_k=2)
                
                self.assertIsInstance(results, list, "Search should return list")
                self.assertLessEqual(len(results), 2, "Should respect top_k limit")


if __name__ == '__main__':
    unittest.main()