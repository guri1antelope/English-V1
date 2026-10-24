"""Review & Mastery Scene for '目指せ英検準2級'

Displays:
- Area progress bars (cleared lessons / total).
- DUO 3.0 Section progress summary.
- AI Spaced Repetition (Forgetting Curve) weak-point quiz trigger.
"""

import pyxel


class SceneReview:
    def __init__(self, app):
        self.app = app

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y

            # 1. 「AIおすすめ復習スタート」ボタン (x: 20, y: 415, 幅280, 高52)
            if 20 <= mx <= 300 and 415 <= my <= 467:
                self._start_ai_review()
                return

            # 2. 「ホームへ戻る」ボタン (x: 20, y: 560, 幅130, 高40)
            if 20 <= mx <= 150 and 560 <= my <= 600:
                self.app.audio.play_se("cancel")
                self.app.change_scene("home")
                return

    def _start_ai_review(self):
        """AI忘却曲線アルゴリズムに基づき、定着度の低い問題を優先抽出してクイズ開始。"""
        slot_data = self.app.get_current_slot_data()
        mastery = slot_data.get("mastery", {}) if slot_data else {}

        # 全問題を収集
        all_questions = []
        for lesson in self.app.quiz_data.get("lessons", []):
            for q in lesson.get("questions", []):
                all_questions.append((q, lesson))

        # 定着スコアでソート（スコアが低い順＝苦手な問題）
        def get_score(item):
            q, _ = item
            qid = q.get("id")
            # 未挑戦問題はスコア60扱い
            return mastery.get(qid, {}).get("score", 60)

        sorted_qs = sorted(all_questions, key=get_score)
        # 上位10問を選択
        selected_pairs = sorted_qs[:10]
        review_questions = [q for q, _ in selected_pairs]

        if review_questions:
            fake_lesson = {
                "id": 999,
                "area_id": 4,
                "title": "AIおすすめ復習特訓",
                "format": "choice",
                "cheat_sheet": {
                    "title": "復習特訓のポイント",
                    "points": [
                        "間違えた問題や忘れかけた問題を優先出題中！",
                        "正解すると定着スコアがアップします。",
                    ],
                },
                "questions": review_questions,
            }
            self.app.audio.play_se("tap")
            self.app.start_quiz(fake_lesson)
        else:
            self.app.audio.play_se("cancel")

    def draw(self):
        pyxel.cls(1)  # 濃紺背景

        # ヘッダー (y: 10〜42, 白枠＋白文字中央揃え)
        pyxel.rect(10, 10, 300, 32, 0)
        pyxel.rectb(10, 10, 300, 32, 7)  # 白枠
        hdr_txt = "進捗状況・復習レッスン"
        hw = self.app.text.measure_text_width(hdr_txt)
        self.app.text.draw_text(10 + (300 - hw) // 2, 18, hdr_txt, 7)

        slot_data = self.app.get_current_slot_data()
        cleared_lessons = (
            slot_data.get("cleared_lessons", {}) if slot_data else {}
        )
        duo_cleared = (
            slot_data.get("duo_cleared_sections", {}) if slot_data else {}
        )
        all_lessons = self.app.quiz_data.get("lessons", [])

        # 1. 学習進捗グラフ (y: 48〜230, 高さ182)
        pyxel.rect(10, 48, 300, 182, 0)
        pyxel.rectb(10, 48, 300, 182, 7)

        self.app.text.draw_text(
            20, 54, "【各コース 学習進捗】", 7, font_type="main"
        )

        # 英検 4エリア
        area_names = ["単語・熟語", "英文法", "会話表現", "実力テスト"]
        for area_id in range(1, 5):
            ay = 76 + (area_id - 1) * 26
            area_ls = [l for l in all_lessons if l.get("area_id") == area_id]
            total_l = len(area_ls)
            cleared_l = sum(
                1
                for l in area_ls
                if cleared_lessons.get(str(l.get("id")), {}).get("cleared")
            )

            rate = cleared_l / max(1, total_l)

            self.app.text.draw_text(
                20, ay, area_names[area_id - 1], 7, font_type="main"
            )

            pyxel.rect(115, ay + 3, 100, 10, 5)
            gw = int(100 * rate)
            if gw > 0:
                pyxel.rect(115, ay + 3, gw, 10, 11 if rate >= 1.0 else 7)

            self.app.text.draw_text(
                222, ay, f"{cleared_l}/{total_l}", 7, font_type="main"
            )

        # DUO 3.0（英検と同じ縦カラム x:20, x:115, x:222 で完全に整列）
        duo_y = 76 + 4 * 26
        duo_sec_cnt = len(duo_cleared)
        duo_rate = duo_sec_cnt / 45.0

        self.app.text.draw_text(
            20, duo_y, "DUO 3.0", 7, font_type="main"
        )
        pyxel.rect(115, duo_y + 3, 100, 10, 5)
        duo_w = int(100 * duo_rate)
        if duo_w > 0:
            pyxel.rect(115, duo_y + 3, duo_w, 10, 11 if duo_rate >= 1.0 else 7)

        self.app.text.draw_text(
            222, duo_y, f"{duo_sec_cnt}/45", 7, font_type="main"
        )

        # 2. AI忘却曲線の状況 (y: 240〜395, 高さ155)
        pyxel.rect(10, 240, 300, 155, 0)
        pyxel.rectb(10, 240, 300, 155, 7)

        mastery = slot_data.get("mastery", {}) if slot_data else {}
        weak_count = sum(1 for m in mastery.values() if m.get("score", 50) < 60)
        mastered_count = sum(
            1 for m in mastery.values() if m.get("score", 50) >= 80
        )

        self.app.text.draw_text(
            20, 248, "【AI 記憶定着スコア】", 7, font_type="main"
        )

        # 階層インデント (x: 24) かつ数値を右寄せ配置して重複を完全防止
        self.app.text.draw_text(
            24, 276, "・マスター済 (80%以上)", 7, font_type="main"
        )
        self.app.text.draw_text(
            230, 276, f"{mastered_count}問", 7, font_type="main"
        )

        self.app.text.draw_text(
            24, 304, "・要復習 (60%未満)", 7, font_type="main"
        )
        self.app.text.draw_text(
            230, 304, f"{weak_count}問", 7, font_type="main"
        )

        # 「・要復習」の「要」の開始位置（x: 40）に完全に揃えてインデント配置
        self.app.text.draw_text_mini(
            40,
            336,
            "※忘却曲線に基づき、苦手な問題を",
            7,
        )
        self.app.text.draw_text_mini(
            40,
            354,
            "　自動選別して復習出題します",
            7,
        )

        # 3. 「AIおすすめ復習スタート」ボタン (y: 415〜467)
        pyxel.rect(20, 415, 280, 52, 0)
        pyxel.rectb(20, 415, 280, 52, 7)
        btn1_str = "▶ AIおすすめ復習を始める！"
        b1w = self.app.text.measure_text_width(btn1_str)
        self.app.text.draw_text(
            20 + (280 - b1w) // 2, 415 + (52 - 16) // 2, btn1_str, 7
        )

        # フッター戻るボタン (y: 560〜600)
        pyxel.rect(20, 560, 130, 40, 0)
        pyxel.rectb(20, 560, 130, 40, 7)
        hw = self.app.text.measure_text_width("◀ ホームへ")
        self.app.text.draw_text(
            20 + (130 - hw) // 2, 560 + (40 - 16) // 2, "◀ ホームへ", 7
        )
