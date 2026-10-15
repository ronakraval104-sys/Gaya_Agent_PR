import os
import tempfile
import unittest
from mini_gaya.memory.instincts import InstinctKeeper

class TestInstincts(unittest.TestCase):
    def test_record_and_retrieve_instinct(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            path = tf.name
        try:
            ik = InstinctKeeper(storage_path=path)
            ik.learn("Always address Ros as Ros in speech synthesis, never R-ZERO-N", category="VOICE", confidence=1.0)
            instincts = ik.list_instincts()
            self.assertEqual(len(instincts), 1)
            self.assertEqual(instincts[0]["category"], "VOICE")
            self.assertIn("Ros", instincts[0]["rule"])
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_export_to_markdown_rules(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            jpath = tf.name
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as mf:
            mpath = mf.name
        try:
            ik = InstinctKeeper(storage_path=jpath)
            ik.learn("Keep ports 4200 (Dashboard) and 8767 (Sprite) isolated", category="PORTS")
            ik.export_markdown(mpath)
            content = open(mpath, "r", encoding="utf-8").read()
            self.assertIn("# Active Agent Instincts", content)
            self.assertIn("PORTS", content)
            self.assertIn("4200", content)
        finally:
            for p in (jpath, mpath):
                if os.path.exists(p):
                    os.remove(p)

if __name__ == "__main__":
    unittest.main()
