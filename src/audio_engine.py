"""Audio Engine for Eiken Pre-2 App.

Handles Pyxel synthesized retro sounds (SE/BGM) and
native English WAV voice playback via browser Audio or Pygame.
"""

import os
import pyxel

try:
    import js  # type: ignore

    IS_WEB = True
except ImportError:
    IS_WEB = False

# PC環境での音声再生用（オプション）
PYGAME_AVAILABLE = False
if not IS_WEB:
    try:
        import pygame

        pygame.mixer.init()
        PYGAME_AVAILABLE = True
    except Exception:
        PYGAME_AVAILABLE = False


class AudioEngine:
    def __init__(self, voices_dir: str = "assets/voices"):
        self.voices_dir = voices_dir
        self.sound_enabled = True
        self.voice_enabled = True
        self._setup_pyxel_sounds()

    def _setup_pyxel_sounds(self):
        """Pyxel内蔵のチップチューン効果音を定義。"""
        # サウンド 0: 決定・タップ音
        pyxel.sounds[0].set(
            notes="c3 e3",
            tones="s p",
            volumes="4 3",
            effects="n n",
            speed=4,
        )

        # サウンド 1: 正解音（ピロリン♪）
        pyxel.sounds[1].set(
            notes="c3 e3 g3 c4",
            tones="s s s s",
            volumes="4 4 4 5",
            effects="n n n n",
            speed=5,
        )

        # サウンド 2: 不正解音（ブブー）
        pyxel.sounds[2].set(
            notes="f2 d2 c2",
            tones="t t t",
            volumes="4 4 3",
            effects="n n f",
            speed=8,
        )

        # サウンド 3: レベルアップ / 進化ファンファーレ
        pyxel.sounds[3].set(
            notes="c2 e2 g2 c3 e3 g3 c4",
            tones="s s s s s s s",
            volumes="4 4 5 5 6 6 7",
            effects="n n n n n n f",
            speed=6,
        )

        # サウンド 4: キャンセル・戻る音
        pyxel.sounds[4].set(
            notes="g2 c2",
            tones="p p",
            volumes="3 2",
            effects="n n",
            speed=5,
        )

        # サウンド 5: もぐもぐ・食べる音
        pyxel.sounds[5].set(
            notes="g3 f3 e3 g3",
            tones="p p p p",
            volumes="4 5 4 6",
            effects="n n n n",
            speed=4,
        )

    def play_se(self, se_type: str):
        """効果音を再生。

        se_type: 'tap', 'correct', 'wrong', 'levelup', 'cancel', 'eat'
        """
        if not self.sound_enabled:
            return

        sound_map = {
            "tap": 0,
            "correct": 1,
            "wrong": 2,
            "levelup": 3,
            "cancel": 4,
            "eat": 5,
        }
        snd_id = sound_map.get(se_type)
        if snd_id is not None:
            pyxel.play(0, snd_id)

    def play_voice(self, filename: str):
        """事前生成された英語音声（WAV/MP3）を再生。"""
        if not self.voice_enabled or not filename:
            return

        filepath = os.path.join(self.voices_dir, filename)

        # 1. Webブラウザ環境
        if IS_WEB:
            try:
                # 単一Audioインスタンス再利用＆フォールバック付き再生
                js_code = (
                    "(function() {"
                    "if (!window._eikenVoiceAudio) { window._eikenVoiceAudio = new Audio(); }"
                    "const audio = window._eikenVoiceAudio;"
                    "audio.pause();"
                    "audio.currentTime = 0;"
                    "const playWith = function(u, fb) {"
                    "  audio.src = u;"
                    "  const p = audio.play();"
                    "  if (p && p.catch) {"
                    "    p.catch(function(e) {"
                    "      if (fb) { playWith(fb, null); }"
                    "      else { console.warn('[Eiken Audio] Play failed:', e); }"
                    "    });"
                    "  }"
                    "};"
                    f"playWith('assets/voices/{filename}', 'app/assets/voices/{filename}');"
                    "})();"
                )
                js.eval(js_code)
            except Exception:
                pass
            return

        # 2. PC環境
        if PYGAME_AVAILABLE and os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
            except Exception:
                pass
