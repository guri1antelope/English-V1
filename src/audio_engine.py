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
            try:
                pyxel.play(0, snd_id)
            except Exception:
                pass

        # Web環境では確実に鳴るWeb Audio APIシンセサイザーで発音
        if IS_WEB:
            self._play_web_synth_se(se_type)

    def _play_web_synth_se(self, se_type: str):
        """ブラウザのWeb Audio APIでレトロピコピコシンセ音を確実に合成・再生。"""
        try:
            import json

            se_json = json.dumps(se_type)
            js_code = (
                "(function() {"
                "const AudioCtx = window.AudioContext || window.webkitAudioContext;"
                "if (!AudioCtx) return;"
                "if (!window._eikenAudioCtx) {"
                "  window._eikenAudioCtx = new AudioCtx();"
                "}"
                "const ctx = window._eikenAudioCtx;"
                "if (ctx.state === 'suspended') {"
                "  ctx.resume();"
                "}"
                "const now = ctx.currentTime;"
                "const playTone = function(freq, type, startTime, duration, vol) {"
                "  const osc = ctx.createOscillator();"
                "  const gain = ctx.createGain();"
                "  osc.type = type;"
                "  osc.frequency.setValueAtTime(freq, startTime);"
                "  gain.gain.setValueAtTime(vol || 0.15, startTime);"
                "  gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);"
                "  osc.connect(gain);"
                "  gain.connect(ctx.destination);"
                "  osc.start(startTime);"
                "  osc.stop(startTime + duration);"
                "};"
                "const se = " + se_json + ";"
                "if (se === 'tap') {"
                "  playTone(580, 'square', now, 0.05, 0.12);"
                "} else if (se === 'correct') {"
                "  playTone(523.25, 'square', now, 0.08, 0.15);"
                "  playTone(659.25, 'square', now + 0.08, 0.08, 0.15);"
                "  playTone(783.99, 'square', now + 0.16, 0.08, 0.15);"
                "  playTone(1046.50, 'square', now + 0.24, 0.18, 0.20);"
                "} else if (se === 'wrong') {"
                "  playTone(180, 'sawtooth', now, 0.15, 0.18);"
                "  playTone(140, 'sawtooth', now + 0.15, 0.25, 0.18);"
                "} else if (se === 'levelup') {"
                "  playTone(261.63, 'square', now, 0.07, 0.15);"
                "  playTone(329.63, 'square', now + 0.07, 0.07, 0.15);"
                "  playTone(392.00, 'square', now + 0.14, 0.07, 0.15);"
                "  playTone(523.25, 'square', now + 0.21, 0.07, 0.15);"
                "  playTone(659.25, 'square', now + 0.28, 0.07, 0.15);"
                "  playTone(783.99, 'square', now + 0.35, 0.07, 0.15);"
                "  playTone(1046.50, 'square', now + 0.42, 0.25, 0.22);"
                "} else if (se === 'cancel') {"
                "  playTone(330, 'triangle', now, 0.06, 0.12);"
                "  playTone(220, 'triangle', now + 0.06, 0.08, 0.12);"
                "} else if (se === 'eat') {"
                "  playTone(392, 'square', now, 0.06, 0.15);"
                "  playTone(330, 'square', now + 0.07, 0.08, 0.15);"
                "}"
                "})();"
            )
            js.eval(js_code)
        except Exception:
            pass

    def speak_text(self, text: str):
        """Web Speech API（ブラウザ標準英語ネイティブ音声）で即座に発音。"""
        if not self.voice_enabled or not text:
            return
        if IS_WEB:
            try:
                import json

                text_json = json.dumps(text)
                js_code = (
                    "(function() {"
                    "if (window.speechSynthesis) {"
                    "  window.speechSynthesis.cancel();"
                    "  const u = new SpeechSynthesisUtterance(" + text_json + ");"
                    "  u.lang = 'en-US';"
                    "  u.rate = 0.95;"
                    "  window.speechSynthesis.speak(u);"
                    "}"
                    "})();"
                )
                js.eval(js_code)
            except Exception:
                pass

    def play_voice(self, filename: str | None = None, text: str | None = None):
        """英語音声を再生。

        filename が指定されている場合は WAV を再生し、
        未指定（またはDUO等でWAV未生成）の場合は speak_text で即座に発音。
        """
        if not self.voice_enabled:
            return
        if not filename and not text:
            return

        # 1. filename が未指定の場合は即座に Web Speech API で発音
        if not filename:
            if text:
                self.speak_text(text)
            return

        filepath = os.path.join(self.voices_dir, filename) if filename else None

        # 2. Webブラウザ環境での WAV 再生
        if IS_WEB:
            try:
                import json

                text_json = json.dumps(text or "")
                file_rel = f"assets/voices/{filename}"
                file_app = f"app/assets/voices/{filename}"

                js_code = (
                    "(function() {"
                    "if (!window._eikenVoiceAudio) { window._eikenVoiceAudio = new Audio(); }"
                    "const audio = window._eikenVoiceAudio;"
                    "audio.pause();"
                    "audio.currentTime = 0;"
                    "const fallbackText = " + text_json + ";"
                    "const speakFallback = function() {"
                    "  if (fallbackText && window.speechSynthesis) {"
                    "    window.speechSynthesis.cancel();"
                    "    const u = new SpeechSynthesisUtterance(fallbackText);"
                    "    u.lang = 'en-US';"
                    "    u.rate = 0.95;"
                    "    window.speechSynthesis.speak(u);"
                    "  }"
                    "};"
                    "const wavFile = " + json.dumps(file_rel) + ";"
                    "const wavFallback = " + json.dumps(file_app) + ";"
                    "audio.onerror = function() {"
                    "  if (audio.src.indexOf('app/') === -1) {"
                    "    audio.src = wavFallback;"
                    "    audio.play().catch(function() { speakFallback(); });"
                    "  } else {"
                    "    speakFallback();"
                    "  }"
                    "};"
                    "audio.src = wavFile;"
                    "const p = audio.play();"
                    "if (p && p.catch) {"
                    "  p.catch(function() { audio.onerror(); });"
                    "}"
                    "})();"
                )
                js.eval(js_code)
            except Exception:
                pass
            return

        # 3. PC環境
        if filepath and PYGAME_AVAILABLE and os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
            except Exception:
                pass
