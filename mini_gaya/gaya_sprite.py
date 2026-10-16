"""Mini Gaya Desktop Companion.
Exposes Mini Gaya sprite classes and forward execution.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import mini_gaya
from mini_gaya import *  # noqa: F401, F403

if __name__ == "__main__":
    sys.exit(mini_gaya.main() if hasattr(mini_gaya, "main") else 0)
