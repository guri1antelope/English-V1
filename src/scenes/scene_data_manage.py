"""Data & Record Management Scene for '目指せ英検準2級'

Handles:
- Player name renaming with 50-on / alphabet keyboard.
- Save data summary (Streak, Lessons cleared, DUO cleared).
- Backup / Transfer code export.
- Safe slot deletion (initialization) with 2-step confirmation modal.
"""

import pyxel
from storage import sanitize_player_name


class SceneDataManage:
    def __init__(self, app):
        self.app = app
        self.mode = "menu"  # "menu" or "name_edit"
        self.input_name = ""
        self.keyboard_mode = "kana"  # "kana" or "alpha"

        self.exported_code = ""
        self.show_code_dialog = False
        self.show_delete_dialog = False
        self.copy_done = False
        self.notice_message = ""
        self.notice_timer = 0

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

    def on_enter(self):
        self.mode = "menu"
        self.show_code_dialog = False
        self.show_delete_dialog = False
        self.copy_done = False
        self.notice_message = ""
        self.notice_timer = 0

    def update(self):
        if self.notice_timer > 0:
            self.notice_timer -= 1

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y

            # 1. スロット消去確認モーダル
            if self.show_delete_dialog:
                # 「消去する」ボタン (x: 40, y: 340, 幅110, 高42)
                if 40 <= mx <= 150 and 340 <= my <= 382:
                    self.app.audio.play_se("wrong")
                    self.app.storage.delete_slot(self.app.current_slot)
                    self.show_delete_dialog = False
                    self.app.change_scene("title")
                    return

                # 「やめる」ボタン (x: 170, y: 340, 幅110, 高42)
                if 170 <= mx <= 280 and 340 <= my <= 382:
                    self.app.audio.play_se("cancel")
                    self.show_delete_dialog = False
                    return
                return

            # 2. 引き継ぎコードダイアログ
            if self.show_code_dialog:
                # 「コピーする」ボタン (x: 25〜165, y: 220〜262)
                if 25 <= mx <= 165 and 220 <= my <= 262:
                    self._copy_to_clipboard(self.exported_code)
                    return
                # 「閉じる」ボタン (x: 175〜295, y: 220〜262)
                if 175 <= mx <= 295 and 220 <= my <= 262:
                    self.show_code_dialog = False
                    self.app.audio.play_se("cancel")
                    return
                # 枠外タップで閉じる (枠: x: 15〜305, y: 110〜285)
                if mx < 15 or mx > 305 or my < 110 or my > 285:
                    self.show_code_dialog = False
                    self.app.audio.play_se("cancel")
                    return
                return

            # 3. 名前編集モード
            if self.mode == "name_edit":
                self._handle_name_edit_click(mx, my)
                return

            # 4. 通常メニューモード
            self._handle_menu_click(mx, my)

    def _handle_menu_click(self, mx: int, my: int):
        # 1. 「なまえを変更する」ボタン (x: 20, y: 216, 幅280, 高46)
        if 20 <= mx <= 300 and 216 <= my <= 262:
            slot_data = self.app.get_current_slot_data()
            self.input_name = slot_data.get("player_name", "") if slot_data else ""
            self.mode = "name_edit"
            self.app.audio.play_se("tap")
            return

        # 2. 「引き継ぎコード発行」ボタン (x: 20, y: 280, 幅280, 高46)
        if 20 <= mx <= 300 and 280 <= my <= 326:
            self.exported_code = self.app.storage.export_backup_code(
                self.app.current_slot
            )
            self.copy_done = False
            self.show_code_dialog = True
            self.app.audio.play_se("tap")
            return

        # 3. 「このスロットを消去（初期化）」ボタン (x: 20, y: 350, 幅280, 高46)
        if 20 <= mx <= 300 and 350 <= my <= 396:
            self.show_delete_dialog = True
            self.app.audio.play_se("cancel")
            return

        # 4. 「ホームへもどる」ボタン (x: 20, y: 550, 幅130, 高40)
        if 20 <= mx <= 150 and 550 <= my <= 590:
            self.app.audio.play_se("cancel")
            self.app.change_scene("home")
            return

    def _handle_name_edit_click(self, mx: int, my: int):
        # キーボードグリッド (y: 350〜510)
        grid = (
            self.kana_grid
            if self.keyboard_mode == "kana"
            else self.alpha_grid
        )
        gw = 28
        gh = 26
        gx_start = 20
        gy_start = 350

        for r, row in enumerate(grid):
            for c, char in enumerate(row):
                kx = gx_start + c * gw
                ky = gy_start + r * gh
                if kx <= mx <= kx + gw - 2 and ky <= my <= ky + gh - 2:
                    if len(self.input_name) < 8:
                        self.input_name += char
                        self.app.audio.play_se("tap")
                    return

        # 「けす」ボタン (20, 485, 幅60, 高34)
        if 20 <= mx <= 80 and 485 <= my <= 519:
            if self.input_name:
                self.input_name = self.input_name[:-1]
                self.app.audio.play_se("cancel")
            return

        # 「切替」ボタン (90, 485, 幅60, 高34)
        if 90 <= mx <= 150 and 485 <= my <= 519:
            self.keyboard_mode = (
                "alpha" if self.keyboard_mode == "kana" else "kana"
            )
            self.app.audio.play_se("tap")
            return

        # 「やめる」ボタン (20, 545, 幅110, 高40)
        if 20 <= mx <= 130 and 545 <= my <= 585:
            self.mode = "menu"
            self.app.audio.play_se("cancel")
            return

        # 「保存する」ボタン (160, 545, 幅140, 高40)
        if 160 <= mx <= 300 and 545 <= my <= 585:
            cleaned = sanitize_player_name(self.input_name)
            slot_data = self.app.get_current_slot_data()
            if slot_data:
                slot_data["player_name"] = cleaned
                self.app.storage.save_slot(self.app.current_slot, slot_data)
                self.notice_message = f"なまえを「{cleaned}」に変更したよ！"
                self.notice_timer = 90
                self.app.audio.play_se("levelup")
            self.mode = "menu"
            return

    def draw(self):
        pyxel.cls(1)  # 濃紺背景

        # ヘッダー (y: 10〜42)
        pyxel.rect(10, 10, 300, 32, 0)
        pyxel.rectb(10, 10, 300, 32, 7)
        hdr_txt = "記録・データ管理"
        hw = self.app.text.measure_text_width(hdr_txt)
        self.app.text.draw_text(10 + (300 - hw) // 2, 18, hdr_txt, 7)

        slot_data = self.app.get_current_slot_data()
        if not slot_data:
            return

        if self.mode == "name_edit":
            self._draw_name_edit(slot_data)
        else:
            self._draw_menu(slot_data)

        # モーダル描画
        if self.show_delete_dialog:
            self._draw_delete_dialog()
        elif self.show_code_dialog:
            self._draw_code_dialog()

    def _draw_menu(self, slot_data: dict):
        pname = slot_data.get("player_name", "たろう")
        streak = slot_data.get("streak", 1)
        partner = slot_data.get("partner", {})
        pid = partner.get("id", 1)
        stg = partner.get("stage", 1)
        plv = partner.get("level", 1)

        cleared_eiken = len(slot_data.get("cleared_lessons", {}))
        cleared_duo = len(slot_data.get("duo_cleared_sections", {}))

        # プレイヤー情報カード (y: 52〜200)
        pyxel.rect(16, 52, 288, 148, 0)
        pyxel.rectb(16, 52, 288, 148, 7)

        # 相棒アイコン
        self.app.graphics.draw_partner(62, 110, pid, stg, mood="happy", scale=2)

        # ステータステキスト
        self.app.text.draw_text(115, 64, f"スロット {self.app.current_slot}", 7)
        self.app.text.draw_text(115, 84, f"なまえ: {pname}", 7)
        self.app.text.draw_text(115, 108, f"相棒Lv: Lv.{plv} (連続{streak}日)", 7)
        self.app.text.draw_text(115, 132, f"英検クリア: {cleared_eiken} / 21", 7)
        self.app.text.draw_text(115, 156, f"DUO制覇: {cleared_duo} / 45", 7)

        # トースト通知（名前変更後など）
        if self.notice_timer > 0 and self.notice_message:
            pyxel.rect(16, 204, 288, 24, 0)
            pyxel.rectb(16, 204, 288, 24, 10)
            nw = self.app.text.measure_text_width(self.notice_message)
            self.app.text.draw_text(16 + (288 - nw) // 2, 208, self.notice_message, 10)

        # 機能ボタン一覧 (均等ピッチで配置)
        # 1. 「なまえを変更する」ボタン (y: 216, 高46)
        pyxel.rect(20, 216, 280, 46, 0)
        pyxel.rectb(20, 216, 280, 46, 7)
        b1_txt = "なまえを変更する"
        w1 = self.app.text.measure_text_width(b1_txt)
        self.app.text.draw_text(20 + (280 - w1) // 2, 231, b1_txt, 7)

        # 2. 「引き継ぎコード発行」ボタン (y: 280, 高46)
        pyxel.rect(20, 280, 280, 46, 0)
        pyxel.rectb(20, 280, 280, 46, 7)
        b2_txt = "引き継ぎコード発行"
        w2 = self.app.text.measure_text_width(b2_txt)
        self.app.text.draw_text(20 + (280 - w2) // 2, 295, b2_txt, 7)

        # 3. 「このスロットを消去（初期化）」ボタン (y: 350, 高46) - 警告枠
        pyxel.rect(20, 350, 280, 46, 0)
        pyxel.rectb(20, 350, 280, 46, 8)  # 赤枠
        b3_txt = "× このスロットを消去（初期化）"
        w3 = self.app.text.measure_text_width(b3_txt)
        self.app.text.draw_text(20 + (280 - w3) // 2, 365, b3_txt, 8)

        # 注意書き (y: 412)
        self.app.text.draw_text(
            26, 412, "※スロットを消去するとデータは元に戻せません。", 7, max_width=268
        )

        # フッター「◀ ホームへもどる」ボタン (y: 550, 高40)
        pyxel.rect(20, 550, 130, 40, 0)
        pyxel.rectb(20, 550, 130, 40, 7)
        hw = self.app.text.measure_text_width("◀ ホームへ")
        self.app.text.draw_text(20 + (130 - hw) // 2, 562, "◀ ホームへ", 7)

    def _draw_name_edit(self, slot_data: dict):
        # 名前編集タイトル
        self.app.text.draw_text(25, 56, "あたらしい なまえ を入力", 7)
        self.app.text.draw_text(25, 80, "（最大8文字まで）", 6)

        # 名前表示枠 (y: 110〜160)
        pyxel.rect(20, 110, 280, 48, 0)
        pyxel.rectb(20, 110, 280, 48, 7)
        display_name = self.input_name if self.input_name else "＿＿＿＿"
        self.app.text.draw_text(35, 126, f"なまえ: {display_name}", 7)

        # 50音／英字キーボード
        grid = (
            self.kana_grid
            if self.keyboard_mode == "kana"
            else self.alpha_grid
        )
        gw = 28
        gh = 26
        gx_start = 20
        gy_start = 350

        for r, row in enumerate(grid):
            for c, char in enumerate(row):
                kx = gx_start + c * gw
                ky = gy_start + r * gh
                pyxel.rect(kx, ky, gw - 2, gh - 2, 0)
                pyxel.rectb(kx, ky, gw - 2, gh - 2, 5)
                self.app.text.draw_text_mini(kx + 7, ky + 5, char, 7)

        # 操作ボタン
        # 「けす」
        pyxel.rect(20, 485, 60, 34, 0)
        pyxel.rectb(20, 485, 60, 34, 7)
        self.app.text.draw_text(34, 494, "けす", 7)

        # 「切替」
        pyxel.rect(90, 485, 60, 34, 0)
        pyxel.rectb(90, 485, 60, 34, 7)
        self.app.text.draw_text(104, 494, "切替", 7)

        # 下部決定ボタン
        # 「やめる」
        pyxel.rect(20, 545, 110, 40, 0)
        pyxel.rectb(20, 545, 110, 40, 7)
        self.app.text.draw_text(48, 557, "やめる", 7)

        # 「保存する」
        pyxel.rect(160, 545, 140, 40, 0)
        pyxel.rectb(160, 545, 140, 40, 7)
        self.app.text.draw_text(194, 557, "保存する ▶", 7)

    def _draw_delete_dialog(self):
        # 画面暗転マスク
        pyxel.rect(10, 180, 300, 220, 0)
        pyxel.rectb(10, 180, 300, 220, 8)  # 赤枠

        # 警告タイトル
        w_title = self.app.text.measure_text_width("【警告】スロットの消去確認")
        self.app.text.draw_text(10 + (300 - w_title) // 2, 200, "【警告】スロットの消去確認", 8)

        # 本文
        msg = f"スロット {self.app.current_slot} のデータを消去しますか？\n集めた相棒やクリア記録は\n完全に失われ、元に戻せません。"
        self.app.text.draw_text(24, 235, msg, 7, max_width=272, line_spacing=4)

        # ボタン
        # 「消去する」
        pyxel.rect(40, 340, 110, 42, 8)
        pyxel.rectb(40, 340, 110, 42, 7)
        self.app.text.draw_text(62, 353, "消去する", 7)

        # 「やめる」
        pyxel.rect(170, 340, 110, 42, 0)
        pyxel.rectb(170, 340, 110, 42, 7)
        self.app.text.draw_text(196, 353, "やめる", 7)

    def _copy_to_clipboard(self, text: str):
        """クリップボードに引き継ぎコードをコピー。"""
        if not text:
            return
        try:
            import js  # type: ignore
            import json

            text_json = json.dumps(text)
            js_code = (
                "(function() {"
                "  if (navigator.clipboard && navigator.clipboard.writeText) {"
                "    navigator.clipboard.writeText(" + text_json + ").catch(function() {"
                "      const ta = document.createElement('textarea');"
                "      ta.value = " + text_json + ";"
                "      document.body.appendChild(ta);"
                "      ta.select();"
                "      document.execCommand('copy');"
                "      document.body.removeChild(ta);"
                "    });"
                "  } else {"
                "    const ta = document.createElement('textarea');"
                "    ta.value = " + text_json + ";"
                "    document.body.appendChild(ta);"
                "    ta.select();"
                "    document.execCommand('copy');"
                "    document.body.removeChild(ta);"
                "  }"
                "})();"
            )
            js.eval(js_code)
        except Exception:
            pass
        self.copy_done = True
        self.app.audio.play_se("correct")

    def _draw_code_dialog(self):
        # ダイアログ枠 (x: 15, y: 110, 幅: 290, 高: 175)
        pyxel.rect(15, 110, 290, 175, 0)
        pyxel.rectb(15, 110, 290, 175, 7)
        pyxel.rectb(16, 111, 288, 173, 11)

        self.app.text.draw_text(25, 122, "【引き継ぎコード】", 7)
        self.app.text.draw_text_mini(
            25, 144, "※別端末・ブラウザのスロットに復元できます", 7
        )

        # コード表示枠
        pyxel.rect(25, 162, 270, 44, 1)
        pyxel.rectb(25, 162, 270, 44, 7)
        short_code = (
            self.exported_code[:28] + "..."
            if len(self.exported_code) > 28
            else self.exported_code
        )
        self.app.text.draw_text_mini(32, 172, short_code, 7)
        self.app.text.draw_text_mini(
            32, 188, f"({len(self.exported_code)}文字の暗号化データ)", 7
        )

        # 1. 「コピー」ボタン (x: 25〜165, y: 220〜262, 幅140, 高42)
        btn_copy_bg = 11 if self.copy_done else 0
        btn_copy_border = 7
        btn_copy_text_col = 0 if self.copy_done else 7
        pyxel.rect(25, 220, 140, 42, btn_copy_bg)
        pyxel.rectb(25, 220, 140, 42, btn_copy_border)
        copy_lbl = "✔ コピー完了！" if self.copy_done else "📋 コードをコピー"
        cw = self.app.text.measure_text_width(copy_lbl)
        self.app.text.draw_text(
            25 + (140 - cw) // 2, 220 + (42 - 16) // 2, copy_lbl, btn_copy_text_col
        )

        # 2. 「閉じる」ボタン (x: 175〜295, y: 220〜262, 幅120, 高42)
        pyxel.rect(175, 220, 120, 42, 0)
        pyxel.rectb(175, 220, 120, 42, 7)
        close_lbl = "閉じる"
        clw = self.app.text.measure_text_width(close_lbl)
        self.app.text.draw_text(
            175 + (120 - clw) // 2, 220 + (42 - 16) // 2, close_lbl, 7
        )
