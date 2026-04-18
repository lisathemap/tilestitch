from __future__ import annotations

import os
from dataclasses import dataclass
from PIL import Image


class RotateError(Exception):
    pass


@dataclass
class RotateConfig:
    angle: float = 0.0
    expand: bool = True
    fill_color: str = "white"

    def __post_init__(self) -> None:
        self.angle = float(self.angle)
        if not (-360.0 <= self.angle <= 360.0):
            raise RotateError(f"angle must be between -360 and 360, got {self.angle}")


def rotate_config_from_env() -> RotateConfig:
    angle = float(os.environ.get("TILESTITCH_ROTATE_ANGLE", "0.0"))
    expand = os.environ.get("TILESTITCH_ROTATE_EXPAND", "true").lower() == "true"
    fill_color = os.environ.get("TILESTITCH_ROTATE_FILL", "white")
    return RotateConfig(angle=angle, expand=expand, fill_color=fill_color)


def rotate_image(image: Image.Image, config: RotateConfig) -> Image.Image:
    if config.angle == 0.0:
        return image
    return image.rotate(
        -config.angle,
        expand=config.expand,
        fillcolor=config.fill_color,
        resample=Image.Resampling.BICUBIC,
    )
