"""Tests for tilestitch.tile_compositor."""
from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_compositor import (
    CompositeLayer,
    CompositorError,
    auto_size,
    composite_layers,
)


def _solid(color: tuple, size: tuple = (256, 256)) -> Image.Image:
    img = Image.new("RGBA", size, color)
    return img


class TestCompositeLayer:
    def test_valid_opacity(self):
        layer = CompositeLayer(image=_solid((255, 0, 0, 255)), offset=(0, 0), opacity=0.5)
        assert layer.opacity == 0.5

    def test_opacity_above_one_raises(self):
        with pytest.raises(CompositorError):
            CompositeLayer(image=_solid((0, 0, 0, 255)), offset=(0, 0), opacity=1.1)

    def test_opacity_below_zero_raises(self):
        with pytest.raises(CompositorError):
            CompositeLayer(image=_solid((0, 0, 0, 255)), offset=(0, 0), opacity=-0.1)


class TestCompositeLayers:
    def test_empty_raises(self):
        with pytest.raises(CompositorError):
            composite_layers([], (256, 256))

    def test_invalid_size_raises(self):
        layer = CompositeLayer(image=_solid((255, 0, 0, 255)), offset=(0, 0))
        with pytest.raises(CompositorError):
            composite_layers([layer], (0, 256))

    def test_returns_image(self):
        layer = CompositeLayer(image=_solid((255, 0, 0, 255)), offset=(0, 0))
        result = composite_layers([layer], (256, 256))
        assert isinstance(result, Image.Image)

    def test_output_size_matches_canvas(self):
        layer = CompositeLayer(image=_solid((255, 0, 0, 255)), offset=(0, 0))
        result = composite_layers([layer], (512, 512))
        assert result.size == (512, 512)

    def test_single_opaque_layer_pixel(self):
        layer = CompositeLayer(image=_solid((200, 100, 50, 255)), offset=(0, 0))
        result = composite_layers([layer], (256, 256))
        pixel = result.getpixel((0, 0))
        assert pixel[0] == 200

    def test_offset_layer_leaves_origin_transparent(self):
        layer = CompositeLayer(image=_solid((255, 0, 0, 255), (128, 128)), offset=(128, 128))
        result = composite_layers([layer], (256, 256))
        assert result.getpixel((0, 0))[3] == 0

    def test_two_layers_composited(self):
        base = CompositeLayer(image=_solid((0, 0, 255, 255)), offset=(0, 0))
        top = CompositeLayer(image=_solid((255, 0, 0, 255)), offset=(0, 0))
        result = composite_layers([base, top], (256, 256))
        assert result.getpixel((0, 0))[0] == 255  # red on top


class TestAutoSize:
    def test_empty_raises(self):
        with pytest.raises(CompositorError):
            auto_size([])

    def test_single_layer(self):
        layer = CompositeLayer(image=_solid((0, 0, 0, 255), (100, 80)), offset=(0, 0))
        assert auto_size([layer]) == (100, 80)

    def test_offset_included(self):
        layer = CompositeLayer(image=_solid((0, 0, 0, 255), (100, 80)), offset=(50, 20))
        assert auto_size([layer]) == (150, 100)

    def test_multiple_layers_max_bounds(self):
        l1 = CompositeLayer(image=_solid((0, 0, 0, 255), (100, 100)), offset=(0, 0))
        l2 = CompositeLayer(image=_solid((0, 0, 0, 255), (50, 50)), offset=(200, 200))
        assert auto_size([l1, l2]) == (250, 250)
