"""Home Scene for '目指せ英検準2級'

Displays companion animal (large animated sprite), status bars (Lv, EXP, Fullness),
feeding interaction, and navigation to Lesson Map and Review.
"""

import pyxel


class SceneHome:
    def __init__(self, app):
        self.app = app
        self.frame = 0
        self.partner_mood = "normal"
        self.mood_timer = 0
        self.jump_timer = 0
        self.heart_timer = 0
        self.speech_bubble = "今日も英語の勉強、一緒に頑張ろう！"
        self.bonus_anim_timer = 0
        self.bonus_exp = 0
        self.bonus_streak = 1

    def on_enter(self):
        """ホーム画面入室時の処理（当日初回ログイン判定とボーナス付与）。"""
        self._check_daily_login_bonus()

    def _check_daily_login_bonus(self):
        slot_data = self.app.get_current_slot_data()
        if not slot_data:
            return

        import datetime
        from storage import get_local_today_str

        today = get_local_today_str()
        last_login = slot_data.get("last_login_date", "")

        # 当日すでに受け取り済みなら何もしない
        if last_login == today:
            return

        # 連続日数の判定
        streak = slot_data.get("streak", 1)
        if last_login:
            try:
                d_last = datetime.date.fromisoformat(last_login)
                d_today = datetime.date.fromisoformat(today)
                diff = (d_today - d_last).days
                if diff == 1:
                    streak += 1
                elif diff > 1:
                    streak = 1
                # diff <= 0 (時計ズレなど) はそのまま維持
            except Exception:
                streak = 1
        else:
            # 初回ログインボーナス（ウェルカムボーナス）
            streak = max(1, streak)

        # 経験値計算: 連続x日目 × 10pt
        bonus_exp = streak * 10
        partner = slot_data.setdefault("partner", {})
        partner["exp"] = partner.get("exp", 0) + bonus_exp
        self._check_level_up(partner)

        # スロット保存
        slot_data["streak"] = streak
        slot_data["last_login_date"] = today
        slot_data["last_date"] = today
        self.app.storage.save_slot(self.app.current_slot, slot_data)

        # 演出用フラグ・タイマー
        self.bonus_anim_timer = 100  # 約3.3秒
        self.bonus_exp = bonus_exp
        self.bonus_streak = streak
        self.partner_mood = "happy"
        self.mood_timer = 100
        self.jump_timer = 30
        self.heart_timer = 50
        self.speech_bubble = f"ログインボーナス！\n連続{streak}日目達成！"
        self.app.audio.play_se("levelup")

    def update(self):
        self.frame += 1

        # アニメーション用タイマー
        if self.jump_timer > 0:
            self.jump_timer -= 1
        if self.heart_timer > 0:
            self.heart_timer -= 1
        if self.bonus_anim_timer > 0:
            self.bonus_anim_timer -= 1

        # 気分のタイマーカウントダウン
        if self.mood_timer > 0:
            self.mood_timer -= 1
            if self.mood_timer == 0:
                self.partner_mood = "normal"
                self.speech_bubble = "次のレッスンに進んでみよう！"

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            self._handle_click(mx, my)

    def _handle_click(self, mx: int, my: int):
        # ログインボーナス演出中のタップで即スキップ
        if self.bonus_anim_timer > 0:
            self.bonus_anim_timer = 0
            self.app.audio.play_se("tap")
            return

        slot_data = self.app.get_current_slot_data()
        if not slot_data:
            return

        partner = slot_data.get("partner", {})
        food = slot_data.get("food_inventory", {})

        # 相棒自身をタップ (cx:160, cy:150, 半径50)
        if 110 <= mx <= 210 and 100 <= my <= 200:
            self.partner_mood = "happy"
            self.mood_timer = 60
            self.speech_bubble = (
                "なでてくれてありがとう！元気が出てきたよ！"
            )
            self.app.audio.play_se("levelup")
            return

        # --- ごはんボタン（3種独立: リンゴ / お肉 / 金のリンゴ） ---
        # 1. リンゴボタン (20, 288, 幅86, 高44) -> +50 EXP, 満腹+20
        if 20 <= mx <= 106 and 288 <= my <= 332:
            if food.get("apple", 0) > 0:
                food["apple"] -= 1
                partner["fullness"] = min(100, partner.get("fullness", 50) + 20)
                partner["exp"] = partner.get("exp", 0) + 50
                self._check_level_up(partner)
                self.app.storage.save_slot(self.app.current_slot, slot_data)

                self.partner_mood = "happy"
                self.mood_timer = 60
                self.jump_timer = 16
                self.heart_timer = 30
                self.speech_bubble = "リンゴおいしい！\nEXPが50アップしたよ！"
                self.app.audio.play_se("eat")
            else:
                self.speech_bubble = "リンゴがないよ。\nレッスンをクリアしてゲットしよう！"
                self.app.audio.play_se("cancel")
            return

        # 2. お肉ボタン (114, 288, 幅86, 高44) -> +120 EXP
        if 114 <= mx <= 200 and 288 <= my <= 332:
            if food.get("meat", 0) > 0:
                food["meat"] -= 1
                partner["exp"] = partner.get("exp", 0) + 120
                self._check_level_up(partner)
                self.app.storage.save_slot(self.app.current_slot, slot_data)

                self.partner_mood = "happy"
                self.mood_timer = 60
                self.jump_timer = 16
                self.heart_timer = 30
                self.speech_bubble = "お肉最高！！\nEXPが120アップしたよ！"
                self.app.audio.play_se("eat")
            else:
                self.speech_bubble = "お肉がないよ。\n★3パーフェクトでゲットできるよ！"
                self.app.audio.play_se("cancel")
            return

        # 3. 金のリンゴボタン (208, 288, 幅92, 高44) -> +300 EXP
        if 208 <= mx <= 300 and 288 <= my <= 332:
            if food.get("golden_apple", 0) > 0:
                food["golden_apple"] -= 1
                partner["exp"] = partner.get("exp", 0) + 300
                self._check_level_up(partner)
                self.app.storage.save_slot(self.app.current_slot, slot_data)

                self.partner_mood = "happy"
                self.mood_timer = 90
                self.jump_timer = 20
                self.heart_timer = 40
                self.speech_bubble = "金のリンゴだ！！\nEXPが300アップしたよ！"
                self.app.audio.play_se("eat")
            else:
                self.speech_bubble = "金のリンゴがないよ。\n今日の挑戦状クリアでゲット！"
                self.app.audio.play_se("cancel")
            return

        # 1. 「★ 今日の挑戦状 (DUO 3問)」ボタン (x:20, y:345, 幅280, 高44)
        if 20 <= mx <= 300 and 345 <= my <= 389:
            import datetime
            today_str = datetime.date.today().isoformat()
            if slot_data.get("last_daily_challenge_date") == today_str:
                self.speech_bubble = "今日の挑戦状はクリア済みだよ！\n明日また挑戦しよう！"
                self.app.audio.play_se("tap")
            else:
                self.app.audio.play_se("levelup")
                self.app.start_daily_duo_quiz()
            return

        # 2. 「レッスンへ進む」ボタン (x:20, y:401, 幅280, 高46)
        if 20 <= mx <= 300 and 401 <= my <= 447:
            self.app.audio.play_se("tap")
            self.app.change_scene("map")
            return

        # 3. 「進捗状況・復習レッスン」ボタン (x:20, y:459, 幅280, 高44)
        if 20 <= mx <= 300 and 459 <= my <= 503:
            self.app.audio.play_se("tap")
            self.app.change_scene("review")
            return

        # 4. 「記録・データ管理」ボタン (x:20, y:515, 幅280, 高42)
        if 20 <= mx <= 300 and 515 <= my <= 557:
            self.app.audio.play_se("tap")
            self.app.change_scene("data_manage")
            return

        # 5. 「スロット選択へもどる」ボタン (x:20, y:572, 幅140, 高38)
        if 20 <= mx <= 160 and 572 <= my <= 610:
            self.app.audio.play_se("cancel")
            self.app.change_scene("title")
            return

    def _check_level_up(self, partner: dict):
        """必要EXPに応じたレベルアップおよび進化判定。"""
        # レベル計算: 100 * level で次のレベル
        cur_lv = partner.get("level", 1)
        cur_exp = partner.get("exp", 0)
        req_exp = cur_lv * 100

        if cur_exp >= req_exp:
            partner["level"] = cur_lv + 1
            partner["exp"] = cur_exp - req_exp
            self.app.audio.play_se("levelup")
            self.speech_bubble = f"レベルアップ！\nLv.{partner['level']} になったよ！"

            # 進化チェック
            stage = partner.get("stage", 1)
            new_stage = stage
            if partner["level"] >= 5 and stage == 1:
                new_stage = 2
            elif partner["level"] >= 15 and stage == 2:
                new_stage = 3
            elif partner["level"] >= 30 and stage == 3:
                new_stage = 4

            if new_stage > stage:
                partner["stage"] = new_stage
                self.speech_bubble = "すごい！\nあたらしい姿に進化したよ！！"

    def draw(self):
        pyxel.cls(1)  # 濃紺背景

        slot_data = self.app.get_current_slot_data()
        if not slot_data:
            return

        player_name = slot_data.get("player_name", "たろう")
        partner = slot_data.get("partner", {})
        food = slot_data.get("food_inventory", {})
        streak = slot_data.get("streak", 1)

        pid = partner.get("id", 1)
        pstage = partner.get("stage", 1)
        plv = partner.get("level", 1)
        pexp = partner.get("exp", 0)
        req_exp = plv * 100
        pfull = partner.get("fullness", 50)

        species_names = ["", "柴犬", "子猫", "ウサギ", "シマリス", "ペンギンヒナ"]
        stage_names = ["", "タマゴ", "幼体", "成体", "究極体"]

        # ヘッダー情報（プレイヤー名・連続日数）
        pyxel.rect(10, 10, 300, 34, 0)
        pyxel.rectb(10, 10, 300, 34, 7)
        self.app.text.draw_text(20, 18, f"{player_name}の部屋", 7)
        self.app.text.draw_text(205, 18, f"連続 {streak}日目", 7)

        # セリフ吹き出し (黒背景・白枠・白文字, 幅300pxでヘッダーと統一・高さ52pxで2行完全収容)
        pyxel.rect(10, 50, 300, 52, 0)
        pyxel.rectb(10, 50, 300, 52, 7)
        self.app.text.draw_text(
            20,
            58,
            self.speech_bubble,
            7,
            max_width=280,
            line_spacing=2,
        )

        # 相棒キャラクター表示（中央・バウンス跳ね演出）
        bounce_y = -8 if self.jump_timer > 8 else (-4 if self.jump_timer > 0 else 0)
        self.app.graphics.draw_partner(
            160,
            160 + bounce_y,
            pid,
            pstage,
            mood="happy" if self.jump_timer > 0 else self.partner_mood,
            frame=self.frame,
            scale=3,
        )

        # もぐもぐハート演出
        if self.heart_timer > 0:
            self.app.text.draw_text_mini(154, 104 + bounce_y, "♥", 8)

        # 相棒の名前と状態 (y: 212 に引き上げてバーとの間に8pxの余白を確保)
        p_title = f"{species_names[pid]} ({stage_names[pstage]})"
        self.app.text.draw_text(
            90, 212, p_title, 7
        )

        # ステータスバー（Lv, EXP）
        pyxel.rect(20, 236, 280, 44, 0)
        pyxel.rectb(20, 236, 280, 44, 7)

        self.app.text.draw_text(26, 250, f"Lv.{plv}", 7)

        # EXPゲージ（幅218pxに拡大してゆったり表示）
        self.app.text.draw_text_mini(72, 242, f"EXP {pexp} / {req_exp}", 7)
        pyxel.rect(72, 258, 218, 10, 5)
        exp_w = int(218 * min(1.0, pexp / max(1, req_exp)))
        if exp_w > 0:
            pyxel.rect(72, 258, exp_w, 10, 11)  # 緑

        # ごはんボタン（3種独立: リンゴ / お肉 / 金のリンゴ）
        apple_cnt = food.get("apple", 0)
        meat_cnt = food.get("meat", 0)
        gold_cnt = food.get("golden_apple", 0)

        # 1. リンゴボタン (20, 288, 幅86, 高44)
        pyxel.rect(20, 288, 86, 44, 0)
        pyxel.rectb(20, 288, 86, 44, 7 if apple_cnt > 0 else 5)
        self.app.text.draw_text_mini(24, 292, f"リンゴ {apple_cnt}個", 7 if apple_cnt > 0 else 5)
        self.app.text.draw_text_mini(24, 312, "+50 EXP", 11 if apple_cnt > 0 else 5)

        # 2. お肉ボタン (114, 288, 幅86, 高44)
        pyxel.rect(114, 288, 86, 44, 0)
        pyxel.rectb(114, 288, 86, 44, 7 if meat_cnt > 0 else 5)
        self.app.text.draw_text_mini(118, 292, f"お肉 {meat_cnt}個", 7 if meat_cnt > 0 else 5)
        self.app.text.draw_text_mini(118, 312, "+120 EXP", 11 if meat_cnt > 0 else 5)

        # 3. 金のリンゴボタン (208, 288, 幅92, 高44)
        pyxel.rect(208, 288, 92, 44, 0)
        pyxel.rectb(208, 288, 92, 44, 7 if gold_cnt > 0 else 5)
        self.app.text.draw_text_mini(212, 292, f"金リンゴ {gold_cnt}個", 7 if gold_cnt > 0 else 5)
        self.app.text.draw_text_mini(212, 312, "+300 EXP", 10 if gold_cnt > 0 else 5)

        # メインナビゲーションボタン (均等間隔12pxで配置)
        # 1. 「今日の挑戦状 (DUO 3問)」 (y: 345, 高44)
        from storage import get_local_today_str
        today_str = get_local_today_str()
        is_daily_cleared = (slot_data.get("last_daily_challenge_date") == today_str)

        if not is_daily_cleared:
            # 未クリア: 黒背景＋白枠(7)＋黄色文字(10)
            pyxel.rect(20, 345, 280, 44, 0)
            pyxel.rectb(20, 345, 280, 44, 7)
            dt_title = "★ 今日の挑戦状 (DUO 3問)"
            dt_sub = "EXP 3倍 + 金のリンゴGET！"
            w_title = self.app.text.measure_text_width(dt_title)
            w_sub = self.app.text.measure_text_width(dt_sub)
            self.app.text.draw_text(20 + (280 - w_title) // 2, 349, dt_title, 10)
            self.app.text.draw_text(20 + (280 - w_sub) // 2, 369, dt_sub, 7)
        else:
            # クリア済み: 黒背景＋白枠(7)＋白文字(7)
            pyxel.rect(20, 345, 280, 44, 0)
            pyxel.rectb(20, 345, 280, 44, 7)
            dt_title = "今日の挑戦状 (クリア済)"
            w_title = self.app.text.measure_text_width(dt_title)
            self.app.text.draw_text(20 + (280 - w_title) // 2, 358, dt_title, 7)

        # 2. 「レッスンへ進む」 (黒背景＋白枠＋白文字, y: 401, 高46)
        pyxel.rect(20, 401, 280, 46, 0)
        pyxel.rectb(20, 401, 280, 46, 7)
        btn_l_text = "▶ レッスンへ進む！"
        w_l = self.app.text.measure_text_width(btn_l_text)
        self.app.text.draw_text(
            20 + (280 - w_l) // 2, 401 + (46 - 16) // 2, btn_l_text, 7
        )

        # 3. 「進捗状況・復習レッスン」 (黒背景＋白枠＋白文字, y: 459, 高44)
        pyxel.rect(20, 459, 280, 44, 0)
        pyxel.rectb(20, 459, 280, 44, 7)
        btn_r1_text = "進捗状況・復習レッスン"
        w_r1 = self.app.text.measure_text_width(btn_r1_text)
        self.app.text.draw_text(
            20 + (280 - w_r1) // 2, 459 + (44 - 16) // 2, btn_r1_text, 7
        )

        # 4. 「記録・データ管理」 (黒背景＋白枠＋白文字, y: 515, 高42)
        pyxel.rect(20, 515, 280, 42, 0)
        pyxel.rectb(20, 515, 280, 42, 7)
        btn_r2_text = "記録・データ管理"
        w_r2 = self.app.text.measure_text_width(btn_r2_text)
        self.app.text.draw_text(
            20 + (280 - w_r2) // 2, 515 + (42 - 16) // 2, btn_r2_text, 7
        )

        # 5. フッターボタン (黒背景＋白枠＋白文字, y: 572, 高38)
        pyxel.rect(20, 572, 140, 38, 0)
        pyxel.rectb(20, 572, 140, 38, 7)
        self.app.text.draw_text(
            28, 582, "◀ スロット選択へ", 7
        )

        # 6. ログインボーナス演出ポップアップ（最前面）
        if self.bonus_anim_timer > 0:
            self._draw_login_bonus_popup()

    def _draw_login_bonus_popup(self):
        """ログインボーナスの華やかなアニメーション演出。"""
        t = self.bonus_anim_timer
        # 最初の20フレームでふわっと上に上昇、後半は定位置
        float_y = max(0, 16 - (100 - t)) if t > 84 else 0
        box_y = 110 - float_y

        # 背景ボックス (黒背景 + 金色/オレンジの二重枠)
        pyxel.rect(18, box_y, 284, 118, 0)
        pyxel.rectb(18, box_y, 284, 118, 10)  # 外枠: 黄色
        pyxel.rectb(20, box_y + 2, 280, 114, 9)  # 内枠: オレンジ

        # タイトルバナー
        title = "★ ログインボーナス ★"
        tw = self.app.text.measure_text_width(title)
        self.app.text.draw_text(18 + (284 - tw) // 2, box_y + 12, title, 10)

        # 連続ログイン日数
        streak_text = f"連続 {self.bonus_streak}日目 達成！"
        sw = self.app.text.measure_text_width(streak_text)
        self.app.text.draw_text(18 + (284 - sw) // 2, box_y + 36, streak_text, 7)

        # 獲得EXPの大きな文字（ピカピカ点滅アニメーション）
        exp_text = f"+{self.bonus_exp} EXP 獲得！"
        ew = self.app.text.measure_text_width(exp_text)
        exp_col = 10 if (self.frame // 4) % 2 == 0 else 7
        self.app.text.draw_text(18 + (284 - ew) // 2, box_y + 64, exp_text, exp_col)

        # タップで閉じる案内
        guide = "- タップして閉じる -"
        gw = self.app.text.measure_text_width(guide)
        self.app.text.draw_text(18 + (284 - gw) // 2, box_y + 92, guide, 6)

        # キラキラ・星パーティクル（周囲に散らす）
        particles = [
            (26, box_y + 16, 10),
            (292, box_y + 18, 9),
            (32, box_y + 95, 11),
            (288, box_y + 90, 10),
            (160 + (self.frame * 3) % 140 - 70, box_y - 6, 7),
        ]
        for px, py, col in particles:
            pyxel.pset(px, py, col)
            pyxel.pset(px + 1, py, col)
            pyxel.pset(px, py + 1, col)
