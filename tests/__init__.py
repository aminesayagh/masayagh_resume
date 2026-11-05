import sys
from pathlib import Path

# The tools are scripts in src/ that import each other by name; make them importable for the tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
