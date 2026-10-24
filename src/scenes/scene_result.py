"""Result Scene for '目指せ英検準2級'

Displays:
- Score (e.g. 8/10), Star Rating (★1〜3), Pass/Fail banner.
- Total EXP earned (Base + Speed bonus).
- Food reward (Apples, Meat).
- Companion Level Up & Evolution fanfare.
- Buttons: 'Back to Map', 'Try Again'.
"""

import pyxel


class SceneResult:
    def __init__(self, app):
        self.app = app
        self.lesson = None
        self.correct_count = 0
        self.total_questions = 10
        self.total_exp = 0
        self.is_passed = False
        self.stars = 0
        self.leveled_up = False
        self.evolved = False
        self.new_level = 1
        self.new_stage = 1
        self.quiz_mode = "eiken"
        self.apples_awarded = 0
        self.meat_awarded = 0
        self.gold_apple_awarded = 0
        self.frame = 0

    def set_result(
        self,
        lesson: dict,
        correct_count: int,
        total_questions: int,
        total_exp: int,
        quiz_mode: str = "eiken",
    ):
        self.lesson = lesson
        self.correct_count = correct_count
        self.total_questions = total_questions
        self.total_exp = total_exp
        self.quiz_mode = quiz_mode
        self.frame = 0
        self.apples_awarded = 0
        self.meat_awarded = 0
        self.gold_apple_awarded = 0

        # 合格判定と星数
        if self.quiz_mode == "daily_duo":
            self.is_passed = True
            if correct_count == total_questions:
                self.stars = 3
            elif correct_count >= 2:
                self.stars = 2
            else:
                self.stars = 1
        elif self.quiz_mode == "duo_section":
            acc = correct_count / max(1, total_questions)
            self.is_passed = acc >= 0.6
            if acc == 1.0:
                self.stars = 3
            elif acc >= 0.8:
                self.stars = 2
            elif acc >= 0.6:
                self.stars = 1
            else:
                self.stars = 0
        else:
            # eiken
            self.is_passed = correct_count >= 8
            if correct_count == 10:
                self.stars = 3
            elif correct_count == 9:
                self.stars = 2
            elif correct_count == 8:
                self.stars = 1
            else:
                self.stars = 0

        # ごほうび付与
        slot_data = self.app.get_current_slot_data()
        if slot_data:
            partner = slot_data.setdefault("partner", {})
            food = slot_data.setdefault("food_inventory", {})

            if self.quiz_mode == "daily_duo":
                import datetime
                self.gold_apple_awarded = 1
                food["golden_apple"] = food.get("golden_apple", 0) + 1
                slot_data["last_daily_challenge_date"] = datetime.date.today().isoformat()
            else:
                # レッスン/セクションクリアのごはん付与
                if self.is_passed:
                    self.apples_awarded = 2
                    food["apple"] = food.get("apple", 0) + 2
                    if self.stars == 3:
                        self.meat_awarded = 1
                        food["meat"] = food.get("meat", 0) + 1
                else:
                    self.apples_awarded = 1
                    food["apple"] = food.get("apple", 0) + 1

            # EXP加算とレベルアップ判定
            old_lv = partner.get("level", 1)
            old_stage = partner.get("stage", 1)
            partner["exp"] = partner.get("exp", 0) + total_exp

            # レベルアップループ
            while True:
                req_exp = partner.get("level", 1) * 100
                if partner.get("exp", 0) >= req_exp:
                    partner["level"] = partner.get("level", 1) + 1
                    partner["exp"] -= req_exp
                else:
                    break

            self.new_level = partner.get("level", 1)
            self.leveled_up = self.new_level > old_lv

            # 進化判定
            new_stage = old_stage
            if self.new_level >= 5 and old_stage == 1:
                new_stage = 2
            elif self.new_level >= 15 and old_stage == 2:
                new_stage = 3
            elif self.new_level >= 30 and old_stage == 3:
                new_stage = 4

            partner["stage"] = new_stage
            self.new_stage = new_stage
            self.evolved = new_stage > old_stage

            # クリア記録の保存
            if self.quiz_mode == "eiken" and self.is_passed:
                lid = str(lesson.get("id"))
                cleared_info = slot_data.setdefault(
                    "cleared_lessons", {}
                ).setdefault(lid, {})
                cleared_info["cleared"] = True
                cleared_info["stars"] = max(
                    cleared_info.get("stars", 0), self.stars
                )
            elif self.quiz_mode == "duo_section" and self.is_passed:
                sid = str(lesson.get("id") or lesson.get("section_id", 1))
                cleared_info = slot_data.setdefault(
                    "duo_cleared_sections", {}
                ).setdefault(sid, {})
                cleared_info["cleared"] = True
                cleared_info["stars"] = max(
                    cleared_info.get("stars", 0), self.stars
                )

            self.app.storage.save_slot(self.app.current_slot, slot_data)

        # サウンド再生
        if self.evolved or self.stars == 3:
            self.app.audio.play_se("levelup")
        elif self.is_passed:
            self.app.audio.play_se("correct")
        else:
            self.app.audio.play_se("wrong")

    def update(self):
        self.frame += 1
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y

            # 左ボタン (x: 20, y: 535, 幅130, 高48)
            if 20 <= mx <= 150 and 535 <= my <= 583:
                self.app.audio.play_se("tap")
                if self.quiz_mode == "daily_duo":
                    self.app.change_scene("home")
                else:
                    self.app.change_scene("map")
                return

            # 右ボタン (x: 170, y: 535, 幅130, 高48)
            if 170 <= mx <= 300 and 535 <= my <= 583:
                self.app.audio.play_se("tap")
                if self.quiz_mode == "daily_duo":
                    self.app.change_scene("home")
                elif self.quiz_mode == "duo_section":
                    self.app.start_duo_quiz(self.lesson)
                else:
                    self.app.start_quiz(self.lesson)
                return

    def draw(self):
        pyxel.cls(1)  # 濃紺背景

        # タイトルバナー (y: 25〜85)
        pyxel.rect(20, 25, 280, 60, 0)

        if self.quiz_mode == "daily_duo":
            pyxel.rectb(20, 25, 280, 60, 10)
            t_title = "今日の挑戦状クリア！"
            t_sub = "EXP大量獲得 ＆ 特別ボーナス！"
            w1 = self.app.text.measure_text_width(t_title)
            w2 = self.app.text.measure_text_width(t_sub)
            self.app.text.draw_text(20 + (280 - w1) // 2, 33, t_title, 10, font_type="main")
            self.app.text.draw_text(20 + (280 - w2) // 2, 57, t_sub, 7, font_type="main")
        elif self.quiz_mode == "duo_section":
            border_col = 11 if self.is_passed else 8
            pyxel.rectb(20, 25, 280, 60, border_col)
            if self.is_passed:
                t_title = "🌲 DUOセクション制覇！"
                star_text = "👑 パーフェクト！ ★★★" if self.stars == 3 else "特訓クリアおめでとう！"
                w1 = self.app.text.measure_text_width(t_title)
                w2 = self.app.text.measure_text_width(star_text)
                self.app.text.draw_text(20 + (280 - w1) // 2, 33, t_title, 11, font_type="main")
                self.app.text.draw_text(20 + (280 - w2) // 2, 57, star_text, 7, font_type="main")
            else:
                t_title = "🌲 特訓しゅうりょう！"
                sub_text = "（合格基準: 60%以上正解）"
                w1 = self.app.text.measure_text_width(t_title)
                w2 = self.app.text.measure_text_width(sub_text)
                self.app.text.draw_text(20 + (280 - w1) // 2, 33, t_title, 8, font_type="main")
                self.app.text.draw_text(20 + (280 - w2) // 2, 57, sub_text, 7, font_type="main")
        else:
            border_col = 11 if self.is_passed else 8
            pyxel.rectb(20, 25, 280, 60, border_col)
            if self.is_passed:
                t_title = "レッスンクリア！"
                star_text = "👑 パーフェクト！ ★★★" if self.stars == 3 else "合格おめでとう！"
                w1 = self.app.text.measure_text_width(t_title)
                w2 = self.app.text.measure_text_width(star_text)
                self.app.text.draw_text(20 + (280 - w1) // 2, 33, t_title, 11, font_type="main")
                self.app.text.draw_text(20 + (280 - w2) // 2, 57, star_text, 7, font_type="main")
            else:
                t_title = "おしい！あと少しで合格！"
                sub_text = "（合格基準: 8問以上正解）"
                w1 = self.app.text.measure_text_width(t_title)
                w2 = self.app.text.measure_text_width(sub_text)
                self.app.text.draw_text(20 + (280 - w1) // 2, 33, t_title, 8, font_type="main")
                self.app.text.draw_text(20 + (280 - w2) // 2, 57, sub_text, 7, font_type="main")

        # スコアカード (y: 95〜235)
        pyxel.rect(20, 95, 280, 135, 0)
        pyxel.rectb(20, 95, 280, 135, 7)

        self.app.text.draw_text(
            35,
            105,
            f"せいかい数 : {self.correct_count} / {self.total_questions} 問",
            7,
            font_type="main",
        )
        self.app.text.draw_text(
            35,
            132,
            f"獲得 EXP   : +{self.total_exp} EXP",
            11,
            font_type="main",
        )

        if self.quiz_mode == "daily_duo":
            self.app.text.draw_text(
                35, 159, "ごほうび   : 金のリンゴ 1個GET", 10, font_type="main"
            )
        else:
            reward_str = f"リンゴ +{self.apples_awarded}"
            if self.meat_awarded > 0:
                reward_str += f"、お肉 +{self.meat_awarded}"
            self.app.text.draw_text(
                35, 159, f"ごほうび   : {reward_str}", 7, font_type="main"
            )

        # レベルアップ・進化メッセージ
        if self.evolved:
            pyxel.rect(30, 190, 260, 28, 0)
            pyxel.rectb(30, 190, 260, 28, 10)
            self.app.text.draw_text(
                55,
                196,
                "あたらしい姿に進化したよ！",
                10,
                font_type="main",
            )
        elif self.leveled_up:
            pyxel.rect(30, 190, 260, 28, 0)
            pyxel.rectb(30, 190, 260, 28, 11)
            self.app.text.draw_text(
                65,
                196,
                f"レベルアップ！ Lv.{self.new_level}",
                11,
                font_type="main",
            )

        # 相棒のアニメーション（中央大きく表示 y: 250〜440）
        slot_data = self.app.get_current_slot_data()
        partner = slot_data.get("partner", {}) if slot_data else {}
        pid = partner.get("id", 1)
        pstage = partner.get("stage", 1)
        mood = "happy" if self.is_passed else "sad"

        self.app.graphics.draw_partner(
            160, 350, pid, pstage, mood=mood, frame=self.frame, scale=3
        )

        # セリフ吹き出し (幅280, 高52, y: 445〜497)
        if self.quiz_mode == "daily_duo":
            speech = "すごい！今日の挑戦状クリア！\nお部屋で金のリンゴを食べてね！"
        elif self.quiz_mode == "duo_section":
            speech = (
                "DUOの例文をしっかり\nマスターできたね！"
                if self.is_passed
                else "難しかったかな？\nもう一度挑戦して復習しよう！"
            )
        else:
            speech = (
                "やったね！\nこの調子でどんどん進もう！"
                if self.is_passed
                else "次はきっと8問以上正解できるよ！"
            )
        pyxel.rect(20, 445, 280, 52, 0)
        pyxel.rectb(20, 445, 280, 52, 7)
        self.app.text.draw_text(
            30, 453, speech, 7, font_type="main", max_width=260, line_spacing=3
        )

        # フッターナビゲーションボタン
        pyxel.rect(20, 535, 130, 48, 0)
        pyxel.rectb(20, 535, 130, 48, 7)
        if self.quiz_mode == "daily_duo":
            btn_left_text = "◀ ホームへ"
            btn_right_text = "お部屋へ ▶"
        elif self.quiz_mode == "duo_section":
            btn_left_text = "◀ DUOの森へ"
            btn_right_text = "もう一回！ ▶"
        else:
            btn_left_text = "◀ マップへ"
            btn_right_text = "もう一回！ ▶"

        w_bl = self.app.text.measure_text_width(btn_left_text)
        self.app.text.draw_text(
            20 + (130 - w_bl) // 2, 550, btn_left_text, 7, font_type="main"
        )

        pyxel.rect(170, 535, 130, 48, 0)
        pyxel.rectb(170, 535, 130, 48, 7)
        w_br = self.app.text.measure_text_width(btn_right_text)
        self.app.text.draw_text(
            170 + (130 - w_br) // 2, 550, btn_right_text, 7, font_type="main"
        )
