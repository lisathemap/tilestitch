"""Channel mixer: adjust per-channel (R, G, B) gain for colour grading."""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from PIL import Image


class ChannelMixerError(Exception):
    """Raised when channel mixer configuration or processing fails."""


@dataclass
class ChannelMixerConfig:
    """Configuration for the channel mixer effect."""

    red: float = 1.0
    green: float = 1.0
    blue: float = 1.0
    enabled: bool = True

    def __post_init__(self) -> None:
        for name, value in (("red", self.red), ("green", self.green), ("blue", self.blue)):
            if not (0.0 <= value <= 4.0):
                raise ChannelMixerError(
                    f"{name} gain must be between 0.0 and 4.0, got {value}"
                )


def channel_mixer_config_from_env() -> ChannelMixerConfig:
    """Build a :class:`ChannelMixerConfig` from environment variables.

    Environment variables:
        TILESTITCH_CHANNEL_MIXER_RED   – red gain   (default 1.0)
        TILESTITCH_CHANNEL_MIXER_GREEN – green gain (default 1.0)
        TILESTITCH_CHANNEL_MIXER_BLUE  – blue gain  (default 1.0)
        TILESTITCH_CHANNEL_MIXER_ENABLED – enabled flag (default true)
    """
    def _float(key: str, default: float) -> float:
        raw = os.environ.get(key, "").strip()
        return float(raw) if raw else default

    def _bool(key: str, default: bool) -> bool:
        raw = os.environ.get(key, "").strip().lower()
        if not raw:
            return default
        if raw in ("1", "true", "yes"):
            return True
        if raw in ("0", "false", "no"):
            return False
        raise ChannelMixerError(f"Invalid boolean for {key}: {raw!r}")

    return ChannelMixerConfig(
        red=_float("TILESTITCH_CHANNEL_MIXER_RED", 1.0),
        green=_float("TILESTITCH_CHANNEL_MIXER_GREEN", 1.0),
        blue=_float("TILESTITCH_CHANNEL_MIXER_BLUE", 1.0),
        enabled=_bool("TILESTITCH_CHANNEL_MIXER_ENABLED", True),
    )


def apply_channel_mixer(image: Image.Image, config: ChannelMixerConfig) -> Image.Image:
    """Apply per-channel gain adjustments to *image*.

    The image is converted to RGBA internally so that alpha is preserved,
    then each RGB channel is multiplied by the corresponding gain value and
    clipped to [0, 255].
    """
    if not config.enabled:
        return image

    original_mode = image.mode
    rgba = image.convert("RGBA")
    arr = np.array(rgba, dtype=np.float32)

    arr[..., 0] = np.clip(arr[..., 0] * config.red,   0, 255)
    arr[..., 1] = np.clip(arr[..., 1] * config.green, 0, 255)
    arr[..., 2] = np.clip(arr[..., 2] * config.blue,  0, 255)

    result = Image.fromarray(arr.astype(np.uint8), mode="RGBA")
    if original_mode != "RGBA":
        result = result.convert(original_mode)
    return result
