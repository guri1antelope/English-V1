"""Lesson Map Scene for '目指せ英検準2級'

Displays 4 Area tabs and scrollable Lesson lists with star ratings and unlock states.
"""

import pyxel


class SceneMap:
    def __init__(self, app):
        self.app = app
        self.mode = "eiken"  # "eiken" or "duo"
        self.selected_area_id = 1
        self.duo_page = 0  # 0: Sec 1-15, 1: Sec 16-30, 2: Sec 31-45
        self.scroll_y = 0

    def update(self):
        # スクロールホイール操作対応
        if pyxel.mouse_wheel != 0:
            self._scroll(-pyxel.mouse_wheel * 25)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            self._handle_click(mx, my)

    def _scroll(self, delta: int):
        if self.mode == "eiken":
            lessons = [
                l
                for l in self.app.quiz_data.get("lessons", [])
                if l.get("area_id") == self.selected_area_id
            ]
            max_scroll = max(0, len(lessons) * 76 - 430)
            self.scroll_y = max(0, min(max_scroll, self.scroll_y + delta))
        else:
            # DUOページ内（15セクション）
            max_scroll = max(0, 15 * 76 - 430)
            self.scroll_y = max(0, min(max_scroll, self.scroll_y + delta))

    def _handle_click(self, mx: int, my: int):
        # 0. 最上部モード切替タブ (y: 8〜34)
        if 8 <= my <= 34:
            if 10 <= mx <= 155:
                if self.mode != "eiken":
                    self.mode = "eiken"
                    self.scroll_y = 0
                    self.app.audio.play_se("tap")
                return
            elif 165 <= mx <= 310:
                if self.mode != "duo":
                    self.mode = "duo"
                    self.scroll_y = 0
                    self.app.audio.play_se("tap")
                return

        # 「ホームへもどる」ボタン (x: 20, y: 570, 幅120, 高40)
        if 20 <= mx <= 140 and 570 <= my <= 610:
            self.app.audio.play_se("cancel")
            self.app.change_scene("home")
            return

        if self.mode == "eiken":
            # 1. 4大エリアタブ (y: 38〜70, 各タブ幅72, x: 10, 86, 162, 238)
            for i in range(1, 5):
                tx = 10 + (i - 1) * 76
                if tx <= mx <= tx + 72 and 38 <= my <= 70:
                    self.selected_area_id = i
                    self.scroll_y = 0
                    self.app.audio.play_se("tap")
                    return

            # 2. レッスンリストのクリック判定 (y: 116〜560)
            if 116 <= my <= 560:
                lessons = [
                    l
                    for l in self.app.quiz_data.get("lessons", [])
                    if l.get("area_id") == self.selected_area_id
                ]
                slot_data = self.app.get_current_slot_data()
                cleared_lessons = (
                    slot_data.get("cleared_lessons", {}) if slot_data else {}
                )

                for idx, lesson in enumerate(lessons):
                    ly = 116 + idx * 76 - self.scroll_y
                    if 10 <= mx <= 310 and ly <= my <= ly + 68:
                        is_unlocked = self._is_lesson_unlocked(
                            lesson, idx, lessons, cleared_lessons
                        )
                        if is_unlocked:
                            self.app.audio.play_se("tap")
                            self.app.start_quiz(lesson)
                        else:
                            self.app.audio.play_se("cancel")
                        return
        else:
            # DUOモード
            # 1. ページタブ (y: 38〜70, 3タブ: 10, 114, 216, 幅94)
            page_xs = [10, 114, 216]
            for p, px in enumerate(page_xs):
                if px <= mx <= px + 94 and 38 <= my <= 70:
                    self.duo_page = p
                    self.scroll_y = 0
                    self.app.audio.play_se("tap")
                    return

            # 2. DUOセクションリストのクリック判定 (y: 116〜560)
            if 116 <= my <= 560:
                sections = self.app.duo_data.get("sections", [])
                start_sec = self.duo_page * 15
                page_sections = sections[start_sec : start_sec + 15]

                for idx, sec in enumerate(page_sections):
                    ly = 116 + idx * 76 - self.scroll_y
                    if 10 <= mx <= 310 and ly <= my <= ly + 68:
                        self.app.audio.play_se("tap")
                        self.app.start_duo_quiz(sec)
                        return

    def _is_lesson_unlocked(
        self, lesson: dict, idx: int, area_lessons: list, cleared_lessons: dict
    ) -> bool:
        lid = str(lesson.get("id"))
        if lesson.get("id") == 1:
            return True
        if lid in cleared_lessons and cleared_lessons[lid].get("cleared"):
            return True
        if idx > 0:
            prev_id = str(area_lessons[idx - 1].get("id"))
            return cleared_lessons.get(prev_id, {}).get("cleared", False)
        return True

    def _split_title(self, full_title: str) -> tuple[str, str]:
        """長いタイトルを主見出し（195px以内）と補足説明にスマート分割する。"""
        if "（" in full_title and "）" in full_title:
            main, rest = full_title.split("（", 1)
            return main.strip(), rest.rstrip("）").strip()
        elif "(" in full_title and ")" in full_title:
            main, rest = full_title.split("(", 1)
            return main.strip(), rest.rstrip(")").strip()
        return full_title, ""

    def draw(self):
        pyxel.cls(1)  # 濃紺背景

        # 最上部モード切替タブ (y: 8〜34)
        # 1. 英検準2級タブ (x: 10, w: 145, h: 26) - 高コントラスト（黒背景＋水色枠＋白文字）
        is_eiken = (self.mode == "eiken")
        eiken_border = 12 if is_eiken else 5
        eiken_col = 7 if is_eiken else 6
        pyxel.rect(10, 8, 145, 26, 0)
        pyxel.rectb(10, 8, 145, 26, eiken_border)
        eiken_lbl = "英検準２級"
        w_e = self.app.text.measure_text_width(eiken_lbl)
        self.app.text.draw_text(10 + (145 - w_e) // 2, 13, eiken_lbl, eiken_col)

        # 2. DUOの森タブ (x: 165, w: 145, h: 26) - 高コントラスト（黒背景＋緑枠＋白文字）
        is_duo = (self.mode == "duo")
        duo_border = 11 if is_duo else 5
        duo_col = 7 if is_duo else 6
        pyxel.rect(165, 8, 145, 26, 0)
        pyxel.rectb(165, 8, 145, 26, duo_border)
        duo_lbl = "DUOの森 (560問)"
        w_d = self.app.text.measure_text_width(duo_lbl)
        self.app.text.draw_text(165 + (145 - w_d) // 2, 13, duo_lbl, duo_col)

        slot_data = self.app.get_current_slot_data()

        if self.mode == "eiken":
            # 4大エリアタブ (y: 38〜70) - 高コントラスト（選択中は黒背景＋水色枠＋白文字）
            tab_names = ["単語", "文法", "会話", "テスト"]
            for i in range(1, 5):
                tx = 10 + (i - 1) * 76
                is_active = self.selected_area_id == i
                border_col = 12 if is_active else 5
                text_col = 7 if is_active else 6

                pyxel.rect(tx, 38, 72, 32, 0)
                pyxel.rectb(tx, 38, 72, 32, border_col)
                name = tab_names[i - 1]
                tw = self.app.text.measure_text_width(name)
                self.app.text.draw_text(tx + (72 - tw) // 2, 46, name, text_col)

            # エリア説明 (y: 74〜110, max_width=288)
            area_info = self.app.quiz_data.get("areas", [])[
                self.selected_area_id - 1
            ]
            self.app.text.draw_text(
                16, 76, area_info.get("description", ""), 6, max_width=288, line_spacing=2
            )

            # レッスンカード一覧 (y: 116〜560) - 高さ68px・ピッチ76pxでゆったり配置
            lessons = [
                l
                for l in self.app.quiz_data.get("lessons", [])
                if l.get("area_id") == self.selected_area_id
            ]
            cleared_lessons = (
                slot_data.get("cleared_lessons", {}) if slot_data else {}
            )

            for idx, lesson in enumerate(lessons):
                ly = 116 + idx * 76 - self.scroll_y
                if ly < 50 or ly > 560:
                    continue

                lid = str(lesson.get("id"))
                is_unlocked = self._is_lesson_unlocked(
                    lesson, idx, lessons, cleared_lessons
                )
                clear_info = cleared_lessons.get(lid, {})
                is_cleared = clear_info.get("cleared", False)
                stars = clear_info.get("stars", 0)

                border_col = 12 if is_cleared else (7 if is_unlocked else 5)
                pyxel.rect(10, ly, 300, 68, 0)
                pyxel.rectb(10, ly, 300, 68, border_col)

                main_title, sub_title = self._split_title(lesson.get("title", ""))
                title_col = 7 if is_unlocked else 5
                # タイトルは幅270pxまで使って1行で美しく表示
                self.app.text.draw_text(
                    18, ly + 8, main_title, title_col, max_width=270
                )

                fmt_str = "4択クイズ" if lesson.get("format") == "choice" else "並び替え"
                self.app.text.draw_text_mini(
                    18, ly + 30, f"{fmt_str} (10問)", 6
                )
                # 獲得報酬の明記 (PixelMplus 12pt)
                self.app.text.draw_text_mini(
                    18, ly + 48, "報酬: 1問100EXP+リンゴ2個 (★3で+肉1個)", 10 if is_unlocked else 5
                )

                if not is_unlocked:
                    self.app.text.draw_text(244, ly + 26, "🔒ロック", 5)
                elif is_cleared:
                    star_str = "★" * stars + "☆" * (3 - stars)
                    self.app.text.draw_text(244, ly + 26, star_str, 10)
                else:
                    self.app.text.draw_text(244, ly + 26, "未クリア", 12)

        else:
            # DUOモード
            # ページタブ (y: 38〜70) - 高コントラスト
            page_labels = ["Sec 01-15", "Sec 16-30", "Sec 31-45"]
            page_xs = [10, 114, 216]
            for p, px in enumerate(page_xs):
                is_active = (self.duo_page == p)
                border_col = 11 if is_active else 5
                text_col = 7 if is_active else 6

                pyxel.rect(px, 38, 94, 32, 0)
                pyxel.rectb(px, 38, 94, 32, border_col)
                lbl = page_labels[p]
                tw = self.app.text.measure_text_width(lbl)
                self.app.text.draw_text(px + (94 - tw) // 2, 46, lbl, text_col)

            # DUO説明文 (y: 74〜110, 2行でスッキリ収めてカードとの衝突を完全防止)
            self.app.text.draw_text(
                16, 76, "DUO 3.0全560例文の特訓ダンジョン！\n重要単語と熟語をマスターしよう！", 6, max_width=288, line_spacing=2
            )

            # DUOセクション一覧 (y: 116〜560) - 高さ68px・ピッチ76px
            sections = self.app.duo_data.get("sections", [])
            start_sec = self.duo_page * 15
            page_sections = sections[start_sec : start_sec + 15]
            duo_cleared = (
                slot_data.get("duo_cleared_sections", {}) if slot_data else {}
            )

            for idx, sec in enumerate(page_sections):
                ly = 116 + idx * 76 - self.scroll_y
                if ly < 50 or ly > 560:
                    continue

                sid = sec.get("id", 1)
                sid_str = str(sid)
                qs = sec.get("questions", [])
                q_count = len(qs)
                clear_info = duo_cleared.get(sid_str, {})
                is_cleared = clear_info.get("cleared", False)
                stars = clear_info.get("stars", 0)

                border_col = 11 if is_cleared else 5
                pyxel.rect(10, ly, 300, 68, 0)
                pyxel.rectb(10, ly, 300, 68, border_col)

                # タイトル
                sec_title = f"Section {sid:02d} ({q_count}問)"
                self.app.text.draw_text(18, ly + 8, sec_title, 7, max_width=270)

                # 例文番号範囲 (波ダッシュを半角ハイフンにして文字抜け解消)
                if qs:
                    s_first = qs[0].get("global_id", 1)
                    s_last = qs[-1].get("global_id", q_count)
                    s_range = f"例文 No.{s_first} - {s_last}"
                else:
                    s_range = "例文"
                self.app.text.draw_text_mini(18, ly + 30, s_range, 6)
                # 獲得報酬の明記 (PixelMplus 12pt)
                self.app.text.draw_text_mini(
                    18, ly + 48, "報酬: 1問100EXP+リンゴ2個 (★3で+肉1個)", 11 if is_cleared else 10
                )

                # ステータス
                if is_cleared:
                    star_str = "★" * stars + "☆" * (3 - stars)
                    self.app.text.draw_text(244, ly + 26, star_str, 10)
                else:
                    self.app.text.draw_text(244, ly + 26, "自由挑戦", 11)

        # フッター帯（スクロール内容が下部に漏れないようにマスク）
        pyxel.rect(0, 565, 320, 75, 1)

        # フッター「◀ ホームへ」ボタン
        pyxel.rect(20, 570, 120, 40, 0)
        pyxel.rectb(20, 570, 120, 40, 5)
        hw = self.app.text.measure_text_width("◀ ホームへ")
        self.app.text.draw_text(
            20 + (120 - hw) // 2, 570 + (40 - 16) // 2, "◀ ホームへ", 6
        )
