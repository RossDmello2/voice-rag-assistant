#!/usr/bin/env python3
"""
Convenience wrapper.
Actual implementation: scripts/manual_tests/graph_smoke.py
Usage: python test_graph.py
"""
import subprocess
import sys


if __name__ == "__main__":
    sys.exit(
        subprocess.call(
            [sys.executable, "scripts/manual_tests/graph_smoke.py"] + sys.argv[1:]
        )
    )
