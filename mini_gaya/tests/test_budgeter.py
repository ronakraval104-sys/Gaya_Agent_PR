import os
import tempfile
import unittest
from mini_gaya.context.budgeter import calculate_pressure, should_warn_pressure, create_session_checkpoint

class TestBudgeter(unittest.TestCase):
    def test_calculate_pressure_healthy(self):
        pressure = calculate_pressure(step_count=10, transcript_bytes=25000, max_steps=50, max_bytes=200000)
        self.assertGreaterEqual(pressure, 0.0)
        self.assertLessEqual(pressure, 0.3)
        self.assertFalse(should_warn_pressure(pressure))

    def test_calculate_pressure_high(self):
        pressure = calculate_pressure(step_count=42, transcript_bytes=180000, max_steps=50, max_bytes=200000)
        self.assertGreaterEqual(pressure, 0.8)
        self.assertTrue(should_warn_pressure(pressure))

    def test_create_session_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            chk_file = create_session_checkpoint(
                conversation_id="conv-123",
                summary="Completed Task 1 & 2",
                open_tasks=["Task 3", "Task 4"],
                output_dir=td
            )
            self.assertTrue(os.path.exists(chk_file))
            content = open(chk_file, "r", encoding="utf-8").read()
            self.assertIn("conv-123", content)
            self.assertIn("Completed Task 1 & 2", content)

if __name__ == "__main__":
    unittest.main()
