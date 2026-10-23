"""Quiz Scene for '目指せ英検準2級'

Handles:
- 4-choice questions & Word Reordering questions.
- Header with Mini Companion, Audio Playback, and Cheat Sheet overlay.
- Speed bonus timer calculation.
- Immediate Feedback modal with explanation.
"""

import random
import time
import pyxel


class SceneQuiz:
    def __init__(self, app):
        self.app = app
        self.lesson = None
        self.questions = []
        self.current_q_idx = 0
        self.correct_count = 0
        self.total_exp_gained = 0

        # クイズ状態: 'answering', 'feedback', 'cheatsheet'
        self.state = "answering"
        self.show_cheatsheet = False
        self.show_translation = False  # 英語ファースト: デフォルト和訳非表示

        # 問題ごとの状態
        self.current_q = None
        self.shuffled_options = []  # 4択用
        self.selected_words = []  # 並び替え解答用
        self.remaining_words = []  # 並び替え残チップ用
        self.q_start_time = 0
        self.last_is_correct = False
        self.last_speed_bonus = 0

        self.quiz_mode = "eiken"  # "eiken", "duo_section", "daily_duo"

        # 相棒リアクション
        self.companion_mood = "normal"
        self.companion_say = "頑張って！"

    def start_quiz(self, lesson: dict):
        self.quiz_mode = "eiken"
        self.lesson = lesson
        all_qs = lesson.get("questions", [])
        # 10問をランダム抽出（プールが10問未満なら全問シャッフル）
        count = min(10, len(all_qs))
        self.questions = (
            random.sample(all_qs, count) if len(all_qs) >= count else all_qs[:]
        )
        random.shuffle(self.questions)

        self.current_q_idx = 0
        self.correct_count = 0
        self.total_exp_gained = 0
        self._load_question(0)

    def start_duo_quiz(self, section: dict):
        self.quiz_mode = "duo_section"
        self.lesson = section
        self.questions = section.get("questions", [])[:]
        self.current_q_idx = 0
        self.correct_count = 0
        self.total_exp_gained = 0
        self._load_question(0)

    def start_daily_duo_quiz(self):
        self.quiz_mode = "daily_duo"
        all_qs = []
        for sec in self.app.duo_data.get("sections", []):
            all_qs.extend(sec.get("questions", []))
        self.questions = (
            random.sample(all_qs, 3) if len(all_qs) >= 3 else all_qs[:]
        )
        self.lesson = {
            "id": "daily_duo",
            "title": "今日の挑戦状 (DUO 3問)",
            "format": "choice",
            "is_daily": True,
            "cheat_sheet": {
                "title": "今日の3問の重要語",
                "points": [
                    f"{q.get('target_word')}: {q.get('translation', '').rstrip('。')}"
                    for q in self.questions
                ],
            },
        }
        self.current_q_idx = 0
        self.correct_count = 0
        self.total_exp_gained = 0
        self._load_question(0)

    def _load_question(self, idx: int):
        self.current_q_idx = idx
        self.current_q = self.questions[idx]
        self.state = "answering"
        self.show_cheatsheet = False
        self.show_translation = False  # 新しい問題では和訳を隠す
        self.companion_mood = "normal"
        self.companion_say = "英語をじっくり読もう！"
        self.q_start_time = time.time()

        q_type = self.current_q.get("type", "choice")
        if q_type == "choice":
            # 4択選択肢のシャッフル
            opts = self.current_q.get("options", [])[:]
            correct_word = opts[self.current_q.get("answer", 0)]
            random.shuffle(opts)
            self.shuffled_options = opts
            # 新しい正解インデックスを記憶
            self.current_correct_idx = opts.index(correct_word)
        elif q_type == "reorder":
            # 並び替え単語チップの準備
            opts = self.current_q.get("options", [])[:]
            indexed_opts = list(enumerate(opts))
            random.shuffle(indexed_opts)
            self.remaining_words = (
                indexed_opts  # [(orig_idx, word), (orig_idx, word), ...]
            )
            self.selected_words = []

    def _get_cheatsheet_geometry(self) -> tuple[int, int]:
        cs = self.lesson.get("cheat_sheet", {}) if self.lesson else {}
        points = cs.get("points", [])
        total_text_h = 0
        for pt in points:
            lines = self.app.text.wrap_text(f"・{pt}", max_width=252)
            total_text_h += len(lines) * 16 + max(0, len(lines) - 1) * 3 + 8
        modal_h = min(540, max(180, 52 + total_text_h + 20))
        modal_y = (640 - modal_h) // 2
        return modal_y, modal_h

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y

            # あんちょこ表示中の場合（右上の[✕]ボタン、または枠外タップで閉じる）
            if self.show_cheatsheet:
                modal_y, modal_h = self._get_cheatsheet_geometry()
                is_close_btn = (260 <= mx <= 300 and modal_y <= my <= modal_y + 40)
                is_outside = (mx < 20 or mx > 300 or my < modal_y or my > modal_y + modal_h)
                if is_close_btn or is_outside:
                    self.show_cheatsheet = False
                    self.app.audio.play_se("cancel")
                return

            # 和訳ポップアップ表示中の場合（右上の[✕]ボタン、またはタップで閉じる）
            if self.show_translation:
                modal_y, modal_h = self._get_translation_geometry()
                is_close_btn = (260 <= mx <= 300 and modal_y <= my <= modal_y + 40)
                is_outside = (mx < 20 or mx > 300 or my < modal_y or my > modal_y + modal_h)
                # ポップアップ内タップまたは枠外タップで閉じる
                self.show_translation = False
                self.app.audio.play_se("cancel")
                return

            # 「◀ やめる」ボタン (x: 6, y: 6, 幅64, 高30) - いつでも安全に中断可能
            if 4 <= mx <= 72 and 4 <= my <= 38:
                self.app.audio.play_se("cancel")
                self._save_abort_exp()
                if self.quiz_mode == "daily_duo":
                    self.app.change_scene("home")
                elif self.lesson and self.lesson.get("id") == 999:
                    self.app.change_scene("review")
                else:
                    self.app.change_scene("map")
                return

            if self.state == "answering":
                self._handle_answering_click(mx, my)
            elif self.state == "feedback":
                self._handle_feedback_click(mx, my)

    def _save_abort_exp(self):
        """途中でやめた場合でも、獲得したEXPを相棒に加算してセーブする。"""
        if self.total_exp_gained <= 0:
            return
        slot_data = self.app.get_current_slot_data()
        if not slot_data:
            return
        partner = slot_data.setdefault("partner", {})
        partner["exp"] = partner.get("exp", 0) + self.total_exp_gained

        # レベルアップ判定
        while True:
            req_exp = partner.get("level", 1) * 100
            if partner.get("exp", 0) >= req_exp:
                partner["level"] = partner.get("level", 1) + 1
                partner["exp"] -= req_exp
            else:
                break

        # 進化判定
        cur_lv = partner.get("level", 1)
        old_stage = partner.get("stage", 1)
        new_stage = old_stage
        if cur_lv >= 5 and old_stage == 1:
            new_stage = 2
        elif cur_lv >= 15 and old_stage == 2:
            new_stage = 3
        elif cur_lv >= 30 and old_stage == 3:
            new_stage = 4
        partner["stage"] = new_stage

        self.app.storage.save_slot(self.app.current_slot, slot_data)
        self.total_exp_gained = 0

    def _handle_answering_click(self, mx: int, my: int):
        # 1. 音声ボタン (x: 214, y: 6, 幅46, 高30)
        if 212 <= mx <= 262 and 4 <= my <= 38:
            audio_file = self.current_q.get("audio_file")
            if audio_file:
                self.app.audio.play_voice(audio_file)
            return

        # 2. 要点あんちょこボタン (x: 266, y: 6, 幅46, 高30)
        has_cheatsheet = bool(self.lesson and self.lesson.get("cheat_sheet"))
        if has_cheatsheet and 264 <= mx <= 314 and 4 <= my <= 38:
            self.show_cheatsheet = True
            self.app.audio.play_se("tap")
            return

        q_type = self.current_q.get("type", "choice")

        # 3. 4択ボタンの判定 (y: 195, 252, 309, 366, 高さ48)
        if q_type == "choice":
            for i in range(len(self.shuffled_options)):
                by = 195 + i * 57
                if 15 <= mx <= 305 and by <= my <= by + 48:
                    self._judge_choice(i)
                    return

            # 和訳トグルボタンの判定 (y: 430〜472)
            if 15 <= mx <= 305 and 430 <= my <= 472:
                self.show_translation = True
                self.app.audio.play_se("tap")
                return

        # 4. 並び替え操作の判定
        elif q_type == "reorder":
            # 残り単語チップのタップ (中段 y: 265〜415)
            for idx, (orig_i, word) in enumerate(self.remaining_words):
                row = idx // 3
                col = idx % 3
                cx = 12 + col * 98
                cy = 265 + row * 44
                if cx <= mx <= cx + 96 and cy <= my <= cy + 38:
                    # 解答スロットへ移動
                    self.selected_words.append((orig_i, word))
                    self.remaining_words.pop(idx)
                    self.app.audio.play_se("tap")
                    return

            # 「ひとつ戻す」ボタン (x: 15, y: 425, 幅90, 高42)
            if 15 <= mx <= 105 and 425 <= my <= 467:
                if self.selected_words:
                    item = self.selected_words.pop()
                    self.remaining_words.append(item)
                    self.app.audio.play_se("cancel")
                return

            # 「これで決定」ボタン (x: 115, y: 425, 幅190, 高42)
            if 115 <= mx <= 305 and 425 <= my <= 467:
                if not self.remaining_words and self.selected_words:
                    self._judge_reorder()
                else:
                    self.companion_say = "すべての単語を並べてから決定を押してね！"
                    self.app.audio.play_se("cancel")
                return

            # 並び替え時の和訳トグルボタン (y: 475〜517)
            if 15 <= mx <= 305 and 475 <= my <= 517:
                self.show_translation = True
                self.app.audio.play_se("tap")
                return

    def _judge_choice(self, chosen_idx: int):
        elapsed = time.time() - self.q_start_time
        speed_bonus = max(0, int(30 - elapsed * 3))

        is_correct = chosen_idx == self.current_correct_idx
        self._record_result(is_correct, speed_bonus)

    def _judge_reorder(self):
        elapsed = time.time() - self.q_start_time
        speed_bonus = max(0, int(30 - elapsed * 3))

        chosen_order = [orig_i for orig_i, w in self.selected_words]
        correct_order = self.current_q.get("answer", [])
        is_correct = chosen_order == correct_order

        self._record_result(is_correct, speed_bonus)

    def _record_result(self, is_correct: bool, speed_bonus: int):
        self.last_is_correct = is_correct
        self.last_speed_bonus = speed_bonus
        self.state = "feedback"

        slot_data = self.app.get_current_slot_data()
        qid = self.current_q.get("id")

        if is_correct:
            self.correct_count += 1
            earned_exp = 100 + speed_bonus
            if self.quiz_mode == "daily_duo":
                earned_exp *= 3
            self.total_exp_gained += earned_exp
            self.companion_mood = "happy"
            self.companion_say = "やったね！大正解！"
            self.app.audio.play_se("correct")

            # AI忘却曲線の更新
            if slot_data and qid:
                m = slot_data.setdefault("mastery", {}).setdefault(
                    qid, {"score": 50, "interval": 1}
                )
                m["score"] = min(100, m.get("score", 50) + 20)
                m["interval"] = m.get("interval", 1) * 2
        else:
            self.companion_mood = "sad"
            self.companion_say = "おしい！解説をよく読んでみよう！"
            self.app.audio.play_se("wrong")

            # 不正解時は忘却スコア低下
            if slot_data and qid:
                m = slot_data.setdefault("mastery", {}).setdefault(
                    qid, {"score": 50, "interval": 1}
                )
                m["score"] = max(0, m.get("score", 50) - 30)
                m["interval"] = 1

        if slot_data:
            self.app.storage.save_slot(self.app.current_slot, slot_data)

    def _handle_feedback_click(self, mx: int, my: int):
        # 「つぎへすすむ」ボタン (x: 20, y: 550, 幅280, 高52)
        if 20 <= mx <= 300 and 550 <= my <= 602:
            self.app.audio.play_se("tap")
            if self.current_q_idx + 1 < len(self.questions):
                self._load_question(self.current_q_idx + 1)
            else:
                # 全問終了 -> リザルト画面へ
                self.app.finish_quiz(
                    self.lesson,
                    self.correct_count,
                    len(self.questions),
                    self.total_exp_gained,
                    quiz_mode=self.quiz_mode,
                )

    def draw(self):
        pyxel.cls(1)  # 統一基調: 濃紺背景

        # ヘッダー (黒背景 ＋ 暗灰枠)
        pyxel.rect(0, 0, 320, 42, 0)
        pyxel.rectb(0, 0, 320, 42, 5)

        # 1. 「◀ やめる」ボタン (x: 6, y: 6, 幅64, 高30) - はみ出し解消
        pyxel.rect(6, 6, 64, 30, 0)
        pyxel.rectb(6, 6, 64, 30, 5)
        self.app.text.draw_text_mini(10, 15, "◀ やめる", 6)

        # 2. ミニ相棒アイコン (x: 76, y: 8)
        slot_data = self.app.get_current_slot_data()
        partner = slot_data.get("partner", {}) if slot_data else {}
        self.app.graphics.draw_partner_mini(
            76,
            8,
            partner.get("id", 1),
            partner.get("stage", 1),
            mood=self.companion_mood,
        )

        # 3. 進捗表示 (12pt mini でスッキリ配置, x: 104, y: 15)
        q_num = self.current_q_idx + 1
        q_total = len(self.questions)
        if self.quiz_mode == "daily_duo":
            self.app.text.draw_text_mini(104, 15, f"挑戦状 {q_num}/{q_total}問", 10)
        elif self.quiz_mode == "duo_section":
            sec_id = self.lesson.get("section_id", 0)
            self.app.text.draw_text_mini(104, 15, f"Sec {sec_id:02d} ({q_num}/{q_total})", 11)
        else:
            self.app.text.draw_text_mini(104, 15, f"第{q_num}問 / 全{q_total}問", 7)

        # 音声ボタン (214, 6, 幅46, 高30) - 統一セカンダリ枠・完全中央揃え
        pyxel.rect(214, 6, 46, 30, 0)
        pyxel.rectb(214, 6, 46, 30, 12)
        self.app.text.draw_text(214 + (46 - 16) // 2, 6 + (30 - 16) // 2, "音", 7)

        # 要点ボタン (266, 6, 幅46, 高30) - 統一セカンダリ枠・完全中央揃え（cheat_sheetが存在する場合のみ）
        if bool(self.lesson and self.lesson.get("cheat_sheet")):
            pyxel.rect(266, 6, 46, 30, 0)
            pyxel.rectb(266, 6, 46, 30, 12)
            self.app.text.draw_text(266 + (46 - 32) // 2, 6 + (30 - 16) // 2, "要点", 7)

        # 問題エリア (y: 48〜185) - 英語ファースト: 英文のみをゆったり表示
        pyxel.rect(12, 48, 296, 138, 0)
        pyxel.rectb(12, 48, 296, 138, 5)

        sentence = self._format_dialogue(self.current_q.get("sentence", ""))
        self.app.text.draw_text(
            22,
            58,
            sentence,
            7,
            font_type="english",
            max_width=276,
            line_spacing=4,
        )

        # 解答エリアの描画
        q_type = self.current_q.get("type", "choice")
        if q_type == "choice":
            self._draw_choice_options()
        elif q_type == "reorder":
            self._draw_reorder_area()

        # 相棒リアクション枠（下部）
        self._draw_companion_footer(q_type)

        # 和訳ヒント展開枠（前面オーバーレイ描画）
        if self.show_translation:
            self._draw_translation_overlay(q_type)

        # 即時フィードバック画面（オーバーレイ）
        if self.state == "feedback":
            self._draw_feedback_modal()

        # 要点あんちょこ画面（オーバーレイ）
        if self.show_cheatsheet:
            self._draw_cheatsheet_modal()

    def _format_dialogue(self, text: str) -> str:
        """会話文のAとBの発言を適切に改行で区切る。"""
        if not text:
            return ""
        import re
        return re.sub(r"(?<!\n)\s*(B[:：])", r"\n\1", text)

    def _get_translation_geometry(self) -> tuple[int, int]:
        """和訳ヒントポップアップの表示位置と高さを動的計算する。"""
        translation = self._format_dialogue(self.current_q.get("translation", ""))
        lines = self.app.text.wrap_text(translation, max_width=240)
        text_h = len(lines) * 16 + max(0, len(lines) - 1) * 4
        modal_h = min(420, max(140, 50 + text_h + 24))
        modal_y = (640 - modal_h) // 2
        return modal_y, modal_h

    def _draw_translation_overlay(self, q_type: str = "choice"):
        """和訳ヒントの展開表示（参考画像準拠: 半透明メッシュ背景＋立体白背景ポップアップ＋緑タイトル＋右上に[✕]ボタン）。"""
        if not self.show_translation:
            return
        translation = self._format_dialogue(self.current_q.get("translation", ""))
        modal_y, modal_h = self._get_translation_geometry()

        # 1. 背後のクイズ画面がうっすら透けて見える半透明ディザリング暗転マスク
        for y in range(0, 640, 2):
            pyxel.rect(0, y, 320, 1, 0)

        # 2. 立体ドロップシャドウ（右下4pxの影）
        pyxel.rect(24, modal_y + 4, 280, modal_h, 0)

        # 3. 白背景カード本体
        pyxel.rect(20, modal_y, 280, modal_h, 7)       # 白背景
        pyxel.rectb(20, modal_y, 280, modal_h, 3)      # 濃緑外枠
        pyxel.rectb(21, modal_y + 1, 278, modal_h - 2, 11) # 明緑内枠

        # 4. タイトル「日本語訳」（中央揃え・濃緑色 3）
        title = "日本語訳"
        tw = self.app.text.measure_text_width(title)
        self.app.text.draw_text(20 + (280 - tw) // 2, modal_y + 12, title, 3)

        # 5. 右上の [ ✕ ] 閉じるボタン（線描画で確実に濃緑の✕を描く）
        pyxel.rect(266, modal_y + 8, 24, 24, 7)
        pyxel.rectb(266, modal_y + 8, 24, 24, 11)
        pyxel.line(272, modal_y + 14, 284, modal_y + 26, 3)
        pyxel.line(273, modal_y + 14, 285, modal_y + 26, 3)
        pyxel.line(272, modal_y + 26, 284, modal_y + 14, 3)
        pyxel.line(273, modal_y + 26, 285, modal_y + 14, 3)

        # 6. 本文（かすれを完全防止するくっきり太字黒文字 0）
        self.app.text.draw_text_bold(
            32, modal_y + 46, translation, 0, max_width=256, line_spacing=4
        )

    def _draw_choice_options(self):
        """4択ボタンの描画 (各 高さ48px, 統一水色枠 12)。"""
        for i, opt in enumerate(self.shuffled_options):
            by = 195 + i * 57
            pyxel.rect(15, by, 290, 48, 0)
            pyxel.rectb(15, by, 290, 48, 12)  # 統一操作カラー: 水色

            opt_text = f"[{i + 1}]  {opt}"
            lines = self.app.text.wrap_text(opt_text, max_width=270, font_type="english")
            text_h = len(lines) * 16 + max(0, len(lines) - 1) * 2
            ty = by + (48 - text_h) // 2
            self.app.text.draw_text(
                22, ty, opt_text, 7, font_type="english", max_width=270, line_spacing=2
            )

        # 和訳ヒントボタン (y: 430〜472, 高さ42px統一)
        pyxel.rect(15, 430, 290, 42, 0)
        pyxel.rectb(15, 430, 290, 42, 12)  # 統一セカンダリ枠
        hint_str = "▼ 日本語訳を見る（ヒント）"
        tw = self.app.text.measure_text_width(hint_str)
        self.app.text.draw_text(
            15 + (290 - tw) // 2, 430 + (42 - 16) // 2, hint_str, 7
        )

    def _draw_reorder_area(self):
        """並び替え解答枠と単語チップの描画。"""
        # 1. 解答スロット枠 (y: 195〜255)
        pyxel.rect(15, 195, 290, 60, 0)
        pyxel.rectb(15, 195, 290, 60, 5)  # 落ち着いた暗灰枠
        self.app.text.draw_text(
            22, 200, "【解答ライン】", 6
        )

        # 並べられた単語 (白文字)
        if self.selected_words:
            ans_str = " ".join([w for _, w in self.selected_words])
            self.app.text.draw_text(
                22,
                222,
                ans_str,
                7,
                max_width=276,
                line_spacing=2,
            )
        else:
            self.app.text.draw_text(
                22,
                222,
                "下の単語チップをタップしてね",
                6,
            )

        # 2. 単語チップ一覧 (y: 265〜415, 幅96px, 高さ38px)
        for idx, (orig_i, word) in enumerate(self.remaining_words):
            row = idx // 3
            col = idx % 3
            cx = 12 + col * 98
            cy = 265 + row * 44
            pyxel.rect(cx, cy, 96, 38, 0)
            pyxel.rectb(cx, cy, 96, 38, 12)  # 水色枠
            tw = self.app.text.measure_text_width(word)
            tx = cx + (96 - tw) // 2 if tw <= 90 else cx + 4
            self.app.text.draw_text(
                tx, cy + 11, word, 7, max_width=90
            )

        # 3. ボタン（戻す・決定）
        # 戻すボタン: 統一キャンセル枠（黒背景＋暗灰枠＋明灰文字）
        pyxel.rect(15, 425, 90, 42, 0)
        pyxel.rectb(15, 425, 90, 42, 5)
        rw = self.app.text.measure_text_width("１つ戻す")
        self.app.text.draw_text(
            15 + (90 - rw) // 2, 425 + (42 - 16) // 2, "１つ戻す", 6
        )

        # 決定ボタン: 有効時は水色プライマリ、無効時も視認可能な明灰文字
        ready = (not self.remaining_words) and bool(self.selected_words)
        btn_bg = 12 if ready else 0
        btn_border = 7 if ready else 5
        btn_text = 0 if ready else 6
        pyxel.rect(115, 425, 190, 42, btn_bg)
        pyxel.rectb(115, 425, 190, 42, btn_border)
        ready_str = "▶ これで決定！"
        ready_w = self.app.text.measure_text_width(ready_str)
        self.app.text.draw_text(
            115 + (190 - ready_w) // 2, 425 + (42 - 16) // 2, ready_str, btn_text
        )

        # 和訳ヒントボタン (y: 475〜517, 高さ42px統一)
        pyxel.rect(15, 475, 290, 42, 0)
        pyxel.rectb(15, 475, 290, 42, 12)  # 統一セカンダリ枠
        hint_str = "▼ 日本語訳を見る（ヒント）"
        tw = self.app.text.measure_text_width(hint_str)
        self.app.text.draw_text(
            15 + (290 - tw) // 2, 475 + (42 - 16) // 2, hint_str, 7
        )

    def _draw_companion_footer(self, q_type: str = "choice"):
        """相棒のセリフとアニメーション。"""
        cy = 535 if q_type == "reorder" else 495
        pyxel.rect(15, cy, 290, 54, 0)
        pyxel.rectb(15, cy, 290, 54, 5)

        slot_data = self.app.get_current_slot_data()
        partner = slot_data.get("partner", {}) if slot_data else {}
        self.app.graphics.draw_partner(
            45,
            cy + 27,
            partner.get("id", 1),
            partner.get("stage", 1),
            mood=self.companion_mood,
            scale=1,
        )

        # 行数に応じた上下完全中央揃え
        lines = self.app.text.wrap_text(self.companion_say, max_width=220)
        text_h = len(lines) * 16 + max(0, len(lines) - 1) * 2
        ty = cy + (54 - text_h) // 2
        self.app.text.draw_text(
            75,
            ty,
            self.companion_say,
            7,
            max_width=220,
            line_spacing=2,
        )

    def _draw_feedback_modal(self):
        """即時フィードバック画面（はみ出し防止構造）。"""
        pyxel.rect(10, 55, 300, 540, 0)
        border_col = 11 if self.last_is_correct else 8
        pyxel.rectb(10, 55, 300, 540, border_col)

        if self.last_is_correct:
            pyxel.rect(20, 68, 280, 40, 11)
            # 中央揃え: 20 + (280 - 80) // 2 = 120
            self.app.text.draw_text(
                120, 80, "◎ 正解！", 0
            )
            bonus_str = (
                f"+{self.last_speed_bonus} EXP"
                if self.last_speed_bonus > 0
                else ""
            )
            # 正解バナーからゆったり18px空けて獲得EXPを表示
            self.app.text.draw_text(
                35, 126, f"獲得: 100 EXP  {bonus_str}", 7
            )
        else:
            pyxel.rect(20, 68, 280, 40, 8)
            # 中央揃え: 20 + (280 - 64) // 2 = 128
            self.app.text.draw_text(
                128, 80, "× 不正解", 7
            )
            self.app.text.draw_text(
                35, 126, "獲得: 0 EXP", 6
            )

        # 正解の英文表示（間隔を30px確保）
        self.app.text.draw_text(
            22, 156, "【正しい英文】", 6
        )
        full_sentence = self.current_q.get("sentence", "")
        q_type = self.current_q.get("type", "choice")
        if q_type == "choice":
            c_word = self.current_q.get("options", [])[
                self.current_q.get("answer", 0)
            ]
            full_sentence = full_sentence.replace("( )", f"[{c_word}]")
        elif q_type == "reorder":
            c_words = [
                self.current_q.get("options", [])[i]
                for i in self.current_q.get("answer", [])
            ]
            full_sentence = full_sentence.replace("( )", " ".join(c_words))

        full_sentence = self._format_dialogue(full_sentence)
        next_y = self.app.text.draw_text(
            22,
            178,
            full_sentence,
            7,
            max_width=276,
            line_spacing=4,
        )

        # 日本語訳（12pxの間隔）
        feedback_trans = self._format_dialogue(self.current_q.get("translation", ""))
        next_y2 = self.app.text.draw_text(
            22,
            next_y + 12,
            f"訳: {feedback_trans}",
            6,
            max_width=276,
            line_spacing=3,
        )

        # ポイント解説（14pxの間隔）
        self.app.text.draw_text(
            22, next_y2 + 14, "【ポイント解説】", 12
        )
        self.app.text.draw_text(
            22,
            next_y2 + 34,
            self.current_q.get("explanation", ""),
            7,
            max_width=276,
            line_spacing=3,
        )

        # 「次へ進む」ボタン (y: 535〜585) - 統一プライマリボタン
        pyxel.rect(20, 535, 280, 48, 12)
        pyxel.rectb(20, 535, 280, 48, 7)
        nxt_str = "▶ 次へ進む！"
        ntw = self.app.text.measure_text_width(nxt_str)
        self.app.text.draw_text(
            20 + (280 - ntw) // 2, 535 + (48 - 16) // 2, nxt_str, 0
        )

    def _draw_cheatsheet_modal(self):
        """要点あんちょこ画面（参考画像準拠: 半透明メッシュ背景＋立体白背景ポップアップ＋緑タイトル＋右上に[✕]ボタン）。"""
        modal_y, modal_h = self._get_cheatsheet_geometry()

        # 1. 背後のクイズ画面がうっすら透けて見える半透明ディザリング暗転マスク
        for y in range(0, 640, 2):
            pyxel.rect(0, y, 320, 1, 0)

        # 2. 立体ドロップシャドウ（右下4pxの影）
        pyxel.rect(24, modal_y + 4, 280, modal_h, 0)

        # 3. 白背景カード本体
        pyxel.rect(20, modal_y, 280, modal_h, 7)       # 白背景
        pyxel.rectb(20, modal_y, 280, modal_h, 3)      # 濃緑外枠
        pyxel.rectb(21, modal_y + 1, 278, modal_h - 2, 11) # 明緑内枠

        cs = self.lesson.get("cheat_sheet", {}) if self.lesson else {}
        title = cs.get("title", "重要ポイント")

        # 4. タイトル（中央揃え・濃緑色 3）
        tw = self.app.text.measure_text_width(title)
        self.app.text.draw_text(20 + (280 - tw) // 2, modal_y + 14, title, 3, max_width=220)

        # 5. 右上の [ ✕ ] 閉じるボタン（線描画で確実に濃緑の✕を描く）
        pyxel.rect(266, modal_y + 8, 24, 24, 7)
        pyxel.rectb(266, modal_y + 8, 24, 24, 11)
        pyxel.line(272, modal_y + 14, 284, modal_y + 26, 3)
        pyxel.line(273, modal_y + 14, 285, modal_y + 26, 3)
        pyxel.line(272, modal_y + 26, 284, modal_y + 14, 3)
        pyxel.line(273, modal_y + 26, 285, modal_y + 14, 3)

        # 6. 本文（かすれを完全防止するくっきり太字黒文字 0）
        cur_y = modal_y + 46
        for pt in cs.get("points", []):
            lines = self.app.text.wrap_text(f"・{pt}", max_width=252)
            for line in lines:
                if cur_y + 16 > modal_y + modal_h - 12:
                    break
                self.app.text.draw_text_bold(30, cur_y, line, 0)
                cur_y += 19
            cur_y += 6
