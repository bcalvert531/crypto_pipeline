# tests/conftest.py
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.absolute()
src_path = project_root / 'src'

print(f"Project root: {project_root}")
print(f"Src path: {src_path}")
print(f"Initial sys.path: {sys.path}")

sys.path.insert(0, str(src_path))

print(f"Updated sys.path: {sys.path}")

# Try importing
try:
    import crypto_pipeline
    print(f"Successfully imported crypto_pipeline from {crypto_pipeline.__file__}")
    import crypto_pipeline.warehouse
    print(f"Successfully imported warehouse from {crypto_pipeline.warehouse.__file__}")
except ImportError as e:
    print(f"Failed to import: {e}")