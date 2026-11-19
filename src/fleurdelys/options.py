"""Validated annotation configuration and deterministic path resolution."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnnotationOptions:
    enable_cmake_annotations: bool = False
    additional_annotations: tuple = ()
    expand_env_variable: bool = False


def configuration(settings, defaults=AnnotationOptions(), base=None, warn=lambda message: None):
    """Read a full snapshot; omitted fields restore startup defaults."""
    if not isinstance(settings, dict):
        warn("Expected an object containing fleurdelys settings.")
        settings = {}
    values = settings.get("fleurdelys", {})
    if not isinstance(values, dict):
        warn("fleurdelys must be an object.")
        values = {}
    enabled = values.get("enableCMakeAnnotations", defaults.enable_cmake_annotations)
    if type(enabled) is not bool:
        warn("fleurdelys.enableCMakeAnnotations must be a boolean; using startup default.")
        enabled = defaults.enable_cmake_annotations
    paths = values.get("additionalAnnotations", defaults.additional_annotations)
    expand_env = values.get("expandEnvVariable", defaults.expand_env_variable)
    if type(expand_env) is not bool:
        warn("fleurdelys.expandEnvVariable must be a boolean; using startup default.")
        expand_env = defaults.expand_env_variable
    if "additionalAnnotations" in values and (not isinstance(paths, list) or any(not isinstance(p, str) for p in paths)):
        warn("fleurdelys.additionalAnnotations must be an array of file paths; using startup default.")
        paths = defaults.additional_annotations
    resolved = []
    for value in paths:
        try:
            path = Path(value)
            if not value:
                raise ValueError("empty path")
            if not path.is_absolute():
                if base is None:
                    warn(f"Cannot resolve annotation '{value}' without a workspace folder; use an absolute path.")
                    continue
                path = Path(base) / path
            path = path.resolve()
            if path not in resolved:
                resolved.append(path)
        except (OSError, ValueError) as error:
            warn(f"Invalid annotation path '{value}': {error}")
    return AnnotationOptions(enabled, tuple(resolved), expand_env)
