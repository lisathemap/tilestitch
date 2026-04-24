"""Tests for tilestitch.tile_channel_mixer."""

from __future__ import annotations

import pytest
from PIL import Image

from tilestitch.tile_channel_mixer import (
    ChannelMixerConfig,
    ChannelMixerError,
    apply_channel_mixer,
    channel_mixer_config_from_env,
)


def _solid(r: int, g: int, b: int, size: int = 4) -> Image.Image:
    return Image.new("RGB", (size, size), (r, g, b))


# ---------------------------------------------------------------------------
# ChannelMixerConfig
# ---------------------------------------------------------------------------

class TestChannelMixerConfig:
    def test_defaults(self):
        cfg = ChannelMixerConfig()
        assert cfg.red == 1.0
        assert cfg.green == 1.0
        assert cfg.blue == 1.0
        assert cfg.enabled is True

    def test_custom_gains_stored(self):
        cfg = ChannelMixerConfig(red=2.0, green=0.5, blue=0.0)
        assert cfg.red == 2.0
        assert cfg.green == 0.5
        assert cfg.blue == 0.0

    def test_zero_gain_valid(self):
        cfg = ChannelMixerConfig(red=0.0)
        assert cfg.red == 0.0

    def test_max_gain_valid(self):
        cfg = ChannelMixerConfig(blue=4.0)
        assert cfg.blue == 4.0

    def test_red_above_max_raises(self):
        with pytest.raises(ChannelMixerError):
            ChannelMixerConfig(red=4.1)

    def test_green_below_zero_raises(self):
        with pytest.raises(ChannelMixerError):
            ChannelMixerConfig(green=-0.1)

    def test_blue_above_max_raises(self):
        with pytest.raises(ChannelMixerError):
            ChannelMixerConfig(blue=5.0)

    def test_enabled_false_stored(self):
        cfg = ChannelMixerConfig(enabled=False)
        assert cfg.enabled is False


# ---------------------------------------------------------------------------
# apply_channel_mixer
# ---------------------------------------------------------------------------

class TestApplyChannelMixer:
    def test_returns_image(self):
        img = _solid(100, 100, 100)
        cfg = ChannelMixerConfig()
        result = apply_channel_mixer(img, cfg)
        assert isinstance(result, Image.Image)

    def test_unity_gain_preserves_pixels(self):
        img = _solid(80, 120, 200)
        cfg = ChannelMixerConfig(red=1.0, green=1.0, blue=1.0)
        result = apply_channel_mixer(img, cfg)
        r, g, b = result.getpixel((0, 0))
        assert r == 80 and g == 120 and b == 200

    def test_zero_red_channel(self):
        img = _solid(200, 100, 50)
        cfg = ChannelMixerConfig(red=0.0)
        result = apply_channel_mixer(img, cfg)
        r, g, b = result.getpixel((0, 0))
        assert r == 0
        assert g == 100
        assert b == 50

    def test_gain_clips_at_255(self):
        img = _solid(200, 200, 200)
        cfg = ChannelMixerConfig(red=4.0)
        result = apply_channel_mixer(img, cfg)
        r, _, _ = result.getpixel((0, 0))
        assert r == 255

    def test_disabled_returns_original(self):
        img = _solid(100, 150, 200)
        cfg = ChannelMixerConfig(red=0.0, enabled=False)
        result = apply_channel_mixer(img, cfg)
        r, g, b = result.getpixel((0, 0))
        assert r == 100 and g == 150 and b == 200

    def test_output_mode_matches_input(self):
        img = _solid(100, 100, 100).convert("RGBA")
        cfg = ChannelMixerConfig()
        result = apply_channel_mixer(img, cfg)
        assert result.mode == "RGBA"

    def test_rgb_input_returns_rgb(self):
        img = _solid(100, 100, 100)
        cfg = ChannelMixerConfig()
        result = apply_channel_mixer(img, cfg)
        assert result.mode == "RGB"


# ---------------------------------------------------------------------------
# channel_mixer_config_from_env
# ---------------------------------------------------------------------------

class TestChannelMixerConfigFromEnv:
    def test_defaults_when_no_env(self, monkeypatch):
        for key in ("TILESTITCH_CHANNEL_MIXER_RED", "TILESTITCH_CHANNEL_MIXER_GREEN",
                    "TILESTITCH_CHANNEL_MIXER_BLUE", "TILESTITCH_CHANNEL_MIXER_ENABLED"):
            monkeypatch.delenv(key, raising=False)
        cfg = channel_mixer_config_from_env()
        assert cfg.red == 1.0 and cfg.green == 1.0 and cfg.blue == 1.0
        assert cfg.enabled is True

    def test_reads_red_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CHANNEL_MIXER_RED", "2.5")
        cfg = channel_mixer_config_from_env()
        assert cfg.red == 2.5

    def test_reads_enabled_false_from_env(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CHANNEL_MIXER_ENABLED", "false")
        cfg = channel_mixer_config_from_env()
        assert cfg.enabled is False

    def test_invalid_enabled_raises(self, monkeypatch):
        monkeypatch.setenv("TILESTITCH_CHANNEL_MIXER_ENABLED", "maybe")
        with pytest.raises(ChannelMixerError):
            channel_mixer_config_from_env()
