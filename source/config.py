"""Shared path configuration for local runs and the persistent Docker volume."""
import os
from pathlib import Path

DATASET_PATH = Path(os.environ.get(
    "DATASET_PATH",
    str(Path(__file__).resolve().parent.parent / "dataset" / "data_pretraitee.csv"),
))
