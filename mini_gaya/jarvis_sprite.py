"""Mini Gaya Desktop Companion (formerly jarvis_sprite.py).
Provides full backward compatibility while delegating execution to mini_gaya.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

if __name__ == "__main__":
    import mini_gaya
    # Forward execution to mini_gaya
    sys.exit(mini_gaya.main() if hasattr(mini_gaya, "main") else 0)
