"""Cross-platform audio support for JustAI Roulette."""

import sys
import math
import threading

_AUDIO_AVAILABLE = False
_sa = None
_winsound = None

try:
    import simpleaudio as sa
    _sa = sa
    _AUDIO_AVAILABLE = True
except ImportError:
    try:
        if sys.platform == "win32":
            import winsound
            _winsound = winsound
            _AUDIO_AVAILABLE = True
    except ImportError:
        pass


def is_audio_available() -> bool:
    """Check if audio playback is available."""
    return _AUDIO_AVAILABLE


def _generate_tone(frequency: float, duration: float, volume: float = 0.3) -> bytes:
    """Generate a simple sine wave tone."""
    try:
        import numpy as np
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t) * volume
        # Apply envelope to avoid clicks
        attack = int(sample_rate * 0.01)
        release = int(sample_rate * 0.01)
        envelope = np.ones_like(tone)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        tone = tone * envelope
        audio = (tone * 32767).astype(np.int16)
        return audio.tobytes()
    except ImportError:
        return b""


def play_sound(sound_name: str, enabled: bool = True) -> None:
    """
    Play a sound effect.

    Args:
        sound_name: One of 'chip_place', 'spin', 'ball_drop', 'win', 'big_win'
        enabled: Whether sound is enabled
    """
    if not enabled or not _AUDIO_AVAILABLE:
        return

    def _play():
        try:
            if _sa:
                # Use simpleaudio with generated tones
                sounds = {
                    "chip_place": (800, 0.05, 0.2),
                    "spin": (400, 0.1, 0.15),
                    "ball_drop": (600, 0.08, 0.25),
                    "win": (523, 0.15, 0.3),       # C5
                    "big_win": (659, 0.3, 0.4),    # E5
                }
                if sound_name in sounds:
                    freq, dur, vol = sounds[sound_name]
                    audio_data = _generate_tone(freq, dur, vol)
                    if audio_data:
                        wave_obj = _sa.WaveObject(audio_data, 1, 2, 44100)
                        wave_obj.play()
            elif _winsound and sys.platform == "win32":
                # Fallback to Windows beep
                freqs = {
                    "chip_place": 800,
                    "spin": 400,
                    "ball_drop": 600,
                    "win": 523,
                    "big_win": 659,
                }
                if sound_name in freqs:
                    _winsound.Beep(freqs[sound_name], 50)
        except Exception:
            pass  # Silently fail if audio doesn't work

    # Play in background thread to avoid blocking UI
    threading.Thread(target=_play, daemon=True).start()
