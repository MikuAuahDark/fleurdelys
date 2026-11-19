from pathlib import Path


# Wheels bundle the annotations inside the package; source checkouts keep them
# at the repository root.
ANNOTATIONS = Path(__file__).resolve().parent / "annotations"
if not ANNOTATIONS.is_dir():
    ANNOTATIONS = Path(__file__).resolve().parents[2] / "annotations"
CORE_ANNOTATIONS = ANNOTATIONS / "core.cmake"
CMAKE_ANNOTATIONS = ANNOTATIONS / "cmake.cmake"
