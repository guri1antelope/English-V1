"""Title & Slot Selection Scene for '目指せ英検準2級'"""

import pyxel
from storage import MAX_SLOTS, get_default_slot_data


class SceneTitle:
    def __init__(self, app):
        self.app = app
        # モード: 'select_slot', 'name_input', 'partner_select', 'backup_dialog'
        self.mode = "select_slot"
        self.selected_slot = 1
        self.input_name = ""
        self.keyboard_mode = "kana"  # 'kana' or 'alpha'
        self.chosen_partner_id = 1
        self.backup_message = ""
        self.startup_grace = 15  # 起動直後の誤タップ防止（約0.5秒間入力をガード）

        # 50音パネル用データ
        self.kana_grid = [
            ["あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ"],
            ["さ", "し", "す", "せ", "そ", "た", "ち", "つ", "て", "と"],
            ["な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "へ", "ほ"],
            ["ま", "み", "む", "め", "も", "や", "ゆ", "よ", "わ", "を"],
            ["ら", "り", "る", "れ", "ろ", "ん", "っ", "ー", "が", "ぎ"],
        ]
        self.alpha_grid = [
            ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
            ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"],
            ["U", "V", "W", "X", "Y", "Z", "-", "_", "!", "?"],
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
        ]

    def update(self):
        if self.startup_grace > 0:
            self.startup_grace -= 1
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            if self.mode == "select_slot":
                self._handle_slot_click(mx, my)
            elif self.mode == "name_input":
                self._handle_name_input_click(mx, my)
            elif self.mode == "partner_select":
                self._handle_partner_select_click(mx, my)

    def _handle_slot_click(self, mx: int, my: int):
        # 4つのスロットカード: 幅280, 高さ50, x:20, sy: 132, 188, 244, 300
        for i in range(1, MAX_SLOTS + 1):
            sy = 132 + (i - 1) * 56
            if 15 <= mx <= 305 and sy - 2 <= my <= sy + 54:
                self.selected_slot = i
                slot_data = self.app.storage.slots.get(i)
                self.app.audio.play_se("tap")
                if slot_data:
                    # 既存データあり -> ゲーム開始
                    self.app.current_slot = i
                    self.app.change_scene("home")
                else:
                    # 空きスロット -> 新規作成（名前入力へ）
                    self.input_name = ""
                    self.mode = "name_input"
                return

    def _handle_name_input_click(self, mx: int, my: int):
        # 50音・英字グリッドのクリック判定 (y: 430〜590)
        grid = (
            self.kana_grid
            if self.keyboard_mode == "kana"
            else self.alpha_grid
        )
        gw = 28
        gh = 26
        gx_start = 20
        gy_start = 430

        for r, row in enumerate(grid):
            for c, char in enumerate(row):
                kx = gx_start + c * gw
                ky = gy_start + r * gh
                if kx <= mx <= kx + gw - 2 and ky <= my <= ky + gh - 2:
                    if len(self.input_name) < 8:
                        self.input_name += char
                        self.app.audio.play_se("tap")
                    return

        # 「けす」ボタン (20, 565, 幅60, 高32)
        if 20 <= mx <= 80 and 565 <= my <= 597:
            if self.input_name:
                self.input_name = self.input_name[:-1]
                self.app.audio.play_se("cancel")
            return

        # 「切替」ボタン (90, 565, 幅60, 高32)
        if 90 <= mx <= 150 and 565 <= my <= 597:
            self.keyboard_mode = (
                "alpha" if self.keyboard_mode == "kana" else "kana"
            )
            self.app.audio.play_se("tap")
            return

        # 「けってい」ボタン (180, 565, 幅120, 高32)
        if 180 <= mx <= 300 and 565 <= my <= 597:
            if not self.input_name:
                self.input_name = f"プレイヤー{self.selected_slot}"
            self.app.audio.play_se("tap")
            self.mode = "partner_select"
            return

    def _handle_partner_select_click(self, mx: int, my: int):
        # 5匹の小動物から選ぶ (y: 180〜480、各ボタン幅260, 高50)
        for p_id in range(1, 6):
            py = 180 + (p_id - 1) * 60
            if 30 <= mx <= 290 and py <= my <= py + 52:
                self.chosen_partner_id = p_id
                self.app.audio.play_se("levelup")
                # セーブデータ作成
                new_data = get_default_slot_data(
                    self.selected_slot, self.input_name, self.chosen_partner_id
                )
                self.app.storage.save_slot(self.selected_slot, new_data)
                self.app.current_slot = self.selected_slot
                self.app.change_scene("home")
                return

    def draw(self):
        pyxel.cls(1)  # 濃紺背景

        if self.mode == "select_slot":
            self._draw_slot_select()
        elif self.mode == "name_input":
            self._draw_name_input()
        elif self.mode == "partner_select":
            self._draw_partner_select()

    def _draw_slot_select(self):
        # 1. タイトル看板（アプリアイコン＋タイトル文字）
        self.app.graphics.draw_title_banner(16, 14, self.app.text)

        # 2. セーブスロット案内
        self.app.text.draw_text(112, 112, "だれがあそぶ？", 7)

        # 3. 4つのセーブスロット
        partner_names = ["", "しばいぬ", "トラネコ", "ウサギ", "シマリス", "ペンギン"]
        for i in range(1, MAX_SLOTS + 1):
            sy = 132 + (i - 1) * 56
            slot_data = self.app.storage.slots.get(i)

            if slot_data:
                # 既存データあり
                pyxel.rect(20, sy, 280, 50, 0)
                pyxel.rectb(20, sy, 280, 50, 12)  # 水色枠
                # アイコン表示
                pid = slot_data.get("partner", {}).get("id", 1)
                stg = slot_data.get("partner", {}).get("stage", 1)
                self.app.graphics.draw_partner(
                    42, sy + 25, pid, stg, mood="happy", scale=1
                )

                pname = slot_data.get("player_name", "たろう")
                plv = slot_data.get("partner", {}).get("level", 1)
                cleared_count = len(slot_data.get("cleared_lessons", {}))

                # 1行目: スロット番号とプレイヤー名（12ptで文字被り防止）
                self.app.text.draw_text_mini(
                    62, sy + 10, f"スロット{i}: {pname}", 7
                )
                # 右上: 「▶ 続きから」アクションバッジ（12ptフォントで上下左右中央配置・高コントラスト）
                pyxel.rect(194, sy + 6, 96, 18, 0)
                pyxel.rectb(194, sy + 6, 96, 18, 12)
                cw = self.app.text.measure_text_width("▶ 続きから", font_type="mini")
                self.app.text.draw_text_mini(
                    194 + (96 - cw) // 2, sy + 6 + (18 - 12) // 2, "▶ 続きから", 7
                )

                # 2行目: 相棒名とクリア状況（進捗も12ptで統一）
                partner_display = partner_names[pid] if 1 <= pid < len(partner_names) else "相棒"
                self.app.text.draw_text_mini(
                    62,
                    sy + 30,
                    f"{partner_display} Lv.{plv}",
                    6,
                )
                self.app.text.draw_text_mini(
                    196,
                    sy + 30,
                    f"進捗: {cleared_count}/21",
                    12,
                )
            else:
                # 空きスロット
                pyxel.rect(20, sy, 280, 50, 0)
                pyxel.rectb(20, sy, 280, 50, 5)  # 暗灰枠
                self.app.text.draw_text_mini(
                    62,
                    sy + 19,
                    f"スロット{i}: ＋ 新規開始",
                    6,
                )

        # 4. ガイド文（完全中央揃え）
        guide_str = "タップしてセーブデータを選択"
        gw = self.app.text.measure_text_width(guide_str)
        self.app.text.draw_text((320 - gw) // 2, 362, guide_str, 6)

        # 5. 下部マスコット集合ステージ (x: 16, 幅: 288 -> 枠範囲: 16〜304)
        self.app.graphics.draw_title_mascots(16, 395, self.app.text)

        # 6. 最下部バージョン表記（PixelMplus 12pt, 枠幅に合わせて左右配置）
        self.app.text.draw_text_mini(16, 602, "Version 1.0.0", 5)
        gw_author = self.app.text.measure_text_width("@2026 gurita", font_type="mini")
        self.app.text.draw_text_mini(304 - gw_author, 602, "@2026 gurita", 5)

    def _draw_name_input(self):
        # 名前入力画面
        self.app.text.draw_text(
            25, 40, f"スロット{self.selected_slot} の なまえ入力", 7
        )
        self.app.text.draw_text(
            25, 65, "（最大8文字まで）", 6
        )

        # 名前表示枠
        pyxel.rect(20, 90, 280, 48, 0)
        pyxel.rectb(20, 90, 280, 48, 12)
        display_name = self.input_name if self.input_name else "＿＿＿＿"
        self.app.text.draw_text(
            40, 106, f"なまえ: {display_name}", 7
        )

        # 50音／英字キーボード
        grid = (
            self.kana_grid
            if self.keyboard_mode == "kana"
            else self.alpha_grid
        )
        gw = 28
        gh = 26
        gx_start = 20
        gy_start = 430

        for r, row in enumerate(grid):
            for c, char in enumerate(row):
                kx = gx_start + c * gw
                ky = gy_start + r * gh
                pyxel.rect(kx, ky, gw - 2, gh - 2, 0)
                pyxel.rectb(kx, ky, gw - 2, gh - 2, 5)
                self.app.text.draw_text(
                    kx + 6, ky + 5, char, 7
                )

        # ボタン類（けす、切替、決定）
        pyxel.rect(20, 565, 60, 36, 0)
        pyxel.rectb(20, 565, 60, 36, 5)  # 統一キャンセル枠
        kw = self.app.text.measure_text_width("けす")
        self.app.text.draw_text(20 + (60 - kw) // 2, 575, "けす", 6)

        pyxel.rect(90, 565, 65, 36, 0)
        pyxel.rectb(90, 565, 65, 36, 5)
        mode_label = "ABC" if self.keyboard_mode == "kana" else "かな"
        mw = self.app.text.measure_text_width(mode_label)
        self.app.text.draw_text(90 + (65 - mw) // 2, 575, mode_label, 7)

        pyxel.rect(170, 565, 130, 36, 12)  # 統一プライマリボタン
        pyxel.rectb(170, 565, 130, 36, 7)
        dw = self.app.text.measure_text_width("決定！")
        self.app.text.draw_text(170 + (130 - dw) // 2, 575, "決定！", 0)

    def _draw_partner_select(self):
        # 相棒選択画面
        self.app.text.draw_text(
            35, 45, "最初の相棒（タマゴ）を選択", 7
        )
        self.app.text.draw_text(
            35, 70, "育てると立派な姿に進化するよ！", 6
        )

        partner_info = [
            (1, "しばいぬのタマゴ", "素直で勇敢な元気な相棒犬"),
            (2, "こねこのタマゴ", "好奇心旺盛な魔法使いネコ"),
            (3, "ウサギのタマゴ", "おだやかで優しい森のウサギ"),
            (4, "シマリスのタマゴ", "すばやい知恵者のシマリス"),
            (5, "ペンギンのタマゴ", "気品あふれる船長ペンギン"),
        ]

        for p_id, p_name, p_desc in partner_info:
            py = 175 + (p_id - 1) * 62
            pyxel.rect(20, py, 280, 54, 0)
            pyxel.rectb(20, py, 280, 54, 12)  # 水色枠

            # タマゴアイコン
            self.app.graphics.draw_partner(
                45, py + 27, p_id, 1, mood="normal", scale=1
            )
            self.app.text.draw_text(
                70, py + 8, p_name, 7, max_width=220
            )
            self.app.text.draw_text(
                70, py + 30, p_desc, 6, max_width=220
            )
