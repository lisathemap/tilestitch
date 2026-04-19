from __future__ import annotations

from dataclasses import dataclass
from PIL import Image, ImageOps


class PosterizeError(ValueError):
    """Raised when posterize configuration is invalid."""


@dataclass
class PosterizeConfig:
    enabled: bool = True
    bits: int = 4  # 1-8 bits per channel

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise PosterizeError("enabled must be a bool")
        if not 1 <= self.bits <= 8:
            raise PosterizeError("bits must be between 1 and 8 inclusive")


def posterize_config_from_env() -> PosterizeConfig:
    import os

    enabled_raw = os.environ.get("TILESTITCH_POSTERIZE_ENABLED", "true")
    bits_raw = os.environ.get("TILESTITCH_POSTERIZE_BITS", "4")

    enabled = enabled_raw.strip().lower() not in ("0", "false", "no")
    try:
        bits = int(bits_raw.strip())
    except ValueError as exc:
        raise PosterizeError(f"Invalid TILESTITCH_POSTERIZE_BITS: {bits_raw!r}") from exc

    return PosterizeConfig(enabled=enabled, bits=bits)


def apply_posterize(image: Image.Image, config: PosterizeConfig) -> Image.Image:
    """Reduce each channel to *bits* bits of colour depth."""
    if not config.enabled:
        return image

    src = image.convert("RGB")
    posterized = ImageOps.posterize(src, config.bits)

    if image.mode == "RGBA":
        result = posterized.convert("RGBA")
        r, g, b, _ = image.split()
        _, _, _, a = image.split()
        result.putalpha(a)
        return result

    return posterized.convert(image.mode)
