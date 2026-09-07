"""Execute the maintained notebook without persisting its outputs into Git."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
notebook = nbformat.read(root / "Clean_Air_OS.ipynb", as_version=4)
nbformat.validate(notebook)
NotebookClient(notebook, timeout=120, kernel_name="python3",
               resources={"metadata": {"path": str(root)}}).execute()
print("Maintained notebook executed successfully from a fresh kernel.")
