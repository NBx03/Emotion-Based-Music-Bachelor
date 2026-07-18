import os
import sys
import tempfile
import types

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("SUNO_TOKEN", "test-token")

_tmp_db_fd, _tmp_db_path = tempfile.mkstemp(suffix=".db")
os.close(_tmp_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db_path}"

# main.py imports image_analysis, which in turn imports image_processing -
# a module that loads CLIP and YOLOv5 at import time. Stub image_analysis
# out *before* main.py is imported anywhere, so this test suite never
# touches torch/transformers/face_recognition and doesn't need them
# installed.
_fake_image_analysis = types.ModuleType("image_analysis")


def _fake_analyze_image(image_bytes):
    return {
        "emotion": "contentment",
        "brightness": 0.6,
        "colorfulness": 0.5,
        "objects": None,
        "face_count": 0,
    }


_fake_image_analysis.analyze_image = _fake_analyze_image
sys.modules["image_analysis"] = _fake_image_analysis


@pytest.fixture(autouse=True)
def _chdir_to_backend(monkeypatch):
    # main.py saves uploads to a relative "uploads/" path, so run every
    # test from backend/ regardless of where pytest was invoked from.
    monkeypatch.chdir(BACKEND_DIR)
