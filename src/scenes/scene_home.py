"""Home Scene for '目指せ英検準2級'

Displays companion animal (large animated sprite), status bars (Lv, EXP, Fullness),
feeding interaction, and navigation to Lesson Map and Review.
"""

import math
import pyxel

COMPANION_SPECIES = ["", "柴犬", "子猫", "ウサギ", "シマリス", "ペンギン"]

# 種族ごとの各成長段階（0..4）の名称と説明
STAGE_INFO = {
    1: [
        ("", ""),
        ("しばいぬのタマゴ", "ふしぎなタマゴ"),
        ("こいぬ", "元気いっぱいの小犬"),
        ("柴犬", "りっぱな成犬"),
        ("探検柴犬", "世界中を旅する名探検家"),
    ],
    2: [
        ("", ""),
        ("トラネコのタマゴ", "ふしぎなタマゴ"),
        ("こねこ", "好奇心旺盛な子猫"),
        ("トラネコ", "堂々としたトラネコ"),
        ("レディキャット", "気品あふれる英国貴婦人猫"),
    ],
    3: [
        ("", ""),
        ("ウサギのタマゴ", "ふしぎなタマゴ"),
        ("こうさぎ", "ぴょんぴょん跳ねる子ウサギ"),
        ("ロップイヤー", "優しいロップイヤー"),
        ("ロイヤルガード", "誇り高き英国の近衛兵ウサギ"),
    ],
    4: [
        ("", ""),
        ("シマリスのタマゴ", "ふしぎなタマゴ"),
        ("こリス", "すばしっこい子リス"),
        ("シマリス", "森のしっかり者リス"),
        ("オックスフォード教授", "英語を極めし知恵の大博士"),
    ],
    5: [
        ("", ""),
        ("ペンギンのタマゴ", "ふしぎなタマゴ"),
        ("ペンギンヒナ", "ふわふわの赤ちゃんペンギン"),
        ("ペンギン成鳥", "立派に泳げる大人のペンギン"),
        ("キャプテンペンギン", "極地を旅する偉大な観測隊長"),
    ],
}


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
        # 進化演出用
        self.evolution_anim = None
        # 成長ロードマップモーダル
        self.show_growth_roadmap = False
        # お食事トコトコアニメーション用
        self.feeding_anim = None

    def on_enter(self):
        """ホーム画面入室時の処理（進化保留チェックとログインボーナス）。"""
        slot_data = self.app.get_current_slot_data()
        if slot_data:
            pending = slot_data.pop("pending_evolution", None)
            if pending:
                self.app.storage.save_slot(self.app.current_slot, slot_data)
                self._trigger_evolution(
                    pending.get("old_stage", 1),
                    pending.get("new_stage", 2),
                    slot_data.get("partner", {}).get("id", 1),
                )
                return
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

        # 進化演出の更新（最優先）
        if self.evolution_anim and self.evolution_anim["active"]:
            self._update_evolution()
            return

        # お食事演出の更新（タップで即スキップ可能）
        if self.feeding_anim:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self._skip_feeding()
                return
            self._update_feeding()
            return

        # 成長ロードマップ表示中はクリックで閉じるのみ
        if self.show_growth_roadmap:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.show_growth_roadmap = False
                self.app.audio.play_se("cancel")
            return

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

    def _trigger_evolution(self, old_stage: int, new_stage: int, pid: int):
        """進化演出を開始。"""
        self.evolution_anim = {
            "active": True,
            "timer": 0,
            "old_stage": old_stage,
            "new_stage": new_stage,
            "pid": pid,
            "fanfare_played": False,
            "ready_to_close": False,
        }

    def _update_evolution(self):
        """進化演出のフレーム更新。"""
        anim = self.evolution_anim
        if not anim:
            return
        anim["timer"] += 1
        t = anim["timer"]

        # フェーズ1: タマゴ・相棒の激しい揺れ＆ヒビ音 (t: 1〜70)
        if t in (15, 35, 55):
            self.app.audio.play_se("egg_crack")

        # フェーズ2: 覚醒・新形態切り替え (t: 80)
        if t == 80:
            slot_data = self.app.get_current_slot_data()
            if slot_data:
                partner = slot_data.setdefault("partner", {})
                partner["stage"] = anim["new_stage"]
                self.app.storage.save_slot(self.app.current_slot, slot_data)
            if not anim["fanfare_played"]:
                self.app.audio.play_se("evolve")
                anim["fanfare_played"] = True

        # フェーズ3: 完了（タップで閉じられる） (t >= 100)
        if t >= 100:
            anim["ready_to_close"] = True

        # タップで終了
        if anim["ready_to_close"] and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            pid = anim["pid"]
            new_stg = anim["new_stage"]
            new_name = STAGE_INFO.get(pid, [("", "")])[new_stg][0]
            self.speech_bubble = f"あたらしい姿に進化したよ！\nこれからよろしくね！"
            self.partner_mood = "happy"
            self.mood_timer = 120
            self.jump_timer = 30
            self.heart_timer = 50
            self.evolution_anim = None
            self.app.audio.play_se("tap")

    def _start_feeding(self, food_type: str, exp_gain: int, full_gain: int, food_name: str):
        """お食事トコトコ演出を開始。"""
        self.feeding_anim = {
            "food_type": food_type,
            "exp_gain": exp_gain,
            "full_gain": full_gain,
            "food_name": food_name,
            "timer": 0,
            "start_x": 65,
            "target_x": 195,
            "plate_x": 240,
            "cy": 160,
        }
        self.speech_bubble = f"{food_name}をみつけたよ！"
        self.app.audio.play_se("tap")

    def _update_feeding(self):
        """お食事演出のフレーム更新。"""
        anim = self.feeding_anim
        if not anim:
            return
        anim["timer"] += 1
        t = anim["timer"]

        if t == 15:
            self.speech_bubble = "トコトコトコ…"
        elif t in (60, 68, 76):
            self.speech_bubble = "もぐもぐ… おいしい！"
            self.app.audio.play_se("eat")
        elif t == 85:
            self.speech_bubble = f"ごちそうさまでした！\nEXPが{anim['exp_gain']}アップしたよ！"
            self.app.audio.play_se("levelup")
        elif t >= 105:
            self._finish_feeding()

    def _finish_feeding(self):
        """お食事演出の完了処理（所持数減算・EXP加算・ステータス保存）。"""
        anim = self.feeding_anim
        if not anim:
            return
        food_type = anim["food_type"]
        exp_gain = anim["exp_gain"]
        full_gain = anim["full_gain"]
        food_name = anim["food_name"]

        slot_data = self.app.get_current_slot_data()
        if slot_data:
            food = slot_data.get("food_inventory", {})
            partner = slot_data.get("partner", {})
            if food.get(food_type, 0) > 0:
                food[food_type] -= 1
                if full_gain > 0:
                    partner["fullness"] = min(100, partner.get("fullness", 50) + full_gain)
                partner["exp"] = partner.get("exp", 0) + exp_gain
                old_lv = partner.get("level", 1)
                self._check_level_up(partner)
                self.app.storage.save_slot(self.app.current_slot, slot_data)
                if partner.get("level", 1) == old_lv and not self.evolution_anim:
                    self.speech_bubble = f"{food_name}おいしかった！\nEXPが{exp_gain}アップしたよ！"

        self.partner_mood = "happy"
        self.mood_timer = 60
        self.jump_timer = 15
        self.heart_timer = 30
        self.feeding_anim = None

    def _skip_feeding(self):
        """タップによるお食事演出の即時スキップ。"""
        self.app.audio.play_se("tap")
        self._finish_feeding()

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

        # 「成長きろく」ボタン（相棒の名前の右横: x:216〜300, y:204〜236）
        if 216 <= mx <= 300 and 204 <= my <= 236:
            self.show_growth_roadmap = True
            self.app.audio.play_se("tap")
            return

        # 相棒自身をタップ (cx:160, cy:150, 半径50)
        if 110 <= mx <= 210 and 100 <= my <= 200:
            self.partner_mood = "happy"
            self.mood_timer = 60
            self.jump_timer = 15
            self.heart_timer = 30
            pid = partner.get("id", 1)
            pstage = partner.get("stage", 1)
            pname = STAGE_INFO.get(pid, [("", "")])[pstage][0]
            self.speech_bubble = f"なでてくれてありがとう！\n元気いっぱいだよ！"
            self.app.audio.play_se("levelup")
            return

        # --- ごはんボタン（3種独立: リンゴ / お肉 / 金のリンゴ） ---
        # 1. リンゴボタン (20, 288, 幅86, 高44) -> +50 EXP, 満腹+20
        if 20 <= mx <= 106 and 288 <= my <= 332:
            if food.get("apple", 0) > 0:
                self._start_feeding("apple", 50, 20, "リンゴ")
            else:
                self.speech_bubble = "リンゴがないよ。\nレッスンをクリアしてゲットしよう！"
                self.app.audio.play_se("cancel")
            return

        # 2. お肉ボタン (114, 288, 幅86, 高44) -> +120 EXP
        if 114 <= mx <= 200 and 288 <= my <= 332:
            if food.get("meat", 0) > 0:
                self._start_feeding("meat", 120, 0, "お肉")
            else:
                self.speech_bubble = "お肉がないよ。\n★3パーフェクトでゲットできるよ！"
                self.app.audio.play_se("cancel")
            return

        # 3. 金のリンゴボタン (208, 288, 幅92, 高44) -> +300 EXP
        if 208 <= mx <= 300 and 288 <= my <= 332:
            if food.get("golden_apple", 0) > 0:
                self._start_feeding("golden_apple", 300, 0, "金のリンゴ")
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
                # 劇的な進化演出をトリガー
                self._trigger_evolution(stage, new_stage, partner.get("id", 1))

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

        # 相棒キャラクター表示（お食事演出中と通常正面の切り替え）
        if self.feeding_anim:
            self._draw_feeding_scene(partner)
        else:
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
        p_title = STAGE_INFO.get(pid, [("", "")])[pstage][0]
        self.app.text.draw_text(24, 212, p_title, 7)

        # 「成長きろく」ボタン（相棒の名前の右横: x:216, y:206, 幅84, 高24）
        pyxel.rect(216, 206, 84, 24, 0)
        pyxel.rectb(216, 206, 84, 24, 12)  # 水色枠
        self.app.text.draw_text_mini(224, 212, "★成長きろく", 12)

        # ステータスバー（Lv, 次の進化目標, EXPゲージ）
        pyxel.rect(20, 236, 280, 44, 0)
        pyxel.rectb(20, 236, 280, 44, 7)

        # 左: レベル表示（16ptフォント・上下中央 y: 249）
        self.app.text.draw_text(26, 249, f"Lv.{plv}", 7)

        # 右上 (y: 241): EXP数値 と 進化目標カウントダウン (横並び・重なりゼロ)
        self.app.text.draw_text_mini(92, 241, f"EXP {pexp}/{req_exp}", 7)

        # 次の成長目標 (Lv.5 / Lv.15 / Lv.30)
        next_lv = 5 if pstage == 1 else (15 if pstage == 2 else (30 if pstage == 3 else None))
        if next_lv:
            rem = max(0, next_lv - plv)
            t_rem = f"(次まであと{rem}Lv)"
            w_rem = self.app.text.measure_text_width(t_rem, font_type="mini")
            self.app.text.draw_text_mini(290 - w_rem, 241, t_rem, 10)
        else:
            t_final = "★最終形態"
            w_final = self.app.text.measure_text_width(t_final, font_type="mini")
            self.app.text.draw_text_mini(290 - w_final, 241, t_final, 11)

        # 右下 (y: 258): EXPゲージバー (幅198pxで綺麗に表示)
        pyxel.rect(92, 258, 198, 12, 5)
        exp_w = int(198 * min(1.0, pexp / max(1, req_exp)))
        if exp_w > 0:
            pyxel.rect(92, 258, exp_w, 12, 11)  # 緑

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

        # 6. ログインボーナス演出ポップアップ
        if self.bonus_anim_timer > 0:
            self._draw_login_bonus_popup()

        # 7. 進化演出カットシーン（最前面）
        if self.evolution_anim and self.evolution_anim["active"]:
            self._draw_evolution_cutscene()

        # 8. 成長ロードマップモーダル（最前面）
        elif self.show_growth_roadmap:
            self._draw_growth_roadmap_modal()

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

    def _draw_evolution_cutscene(self):
        """ドラマチックな進化演出カットシーン（揺れ・ヒビ・光・新形態登場）。"""
        anim = self.evolution_anim
        if not anim:
            return
        t = anim["timer"]
        pid = anim["pid"]
        old_stg = anim["old_stage"]
        new_stg = anim["new_stage"]

        old_name = STAGE_INFO.get(pid, [("", "")])[old_stg][0]
        new_name = STAGE_INFO.get(pid, [("", "")])[new_stg][0]
        new_desc = STAGE_INFO.get(pid, [("", "")])[new_stg][1]

        # 画面全域を黒の暗幕で覆う
        pyxel.rect(0, 0, 320, 640, 0)

        # 背景の星屑パーティクル
        for i in range(16):
            sx = (i * 37 + (self.frame * 2)) % 320
            sy = (i * 53 + (self.frame * 3)) % 640
            pyxel.pset(sx, sy, 7 if (i + self.frame // 4) % 2 == 0 else 10)

        if t < 75:
            # --- フェーズ1: 予兆・相棒の激しい揺れ＆ヒビ音 ---
            pyxel.rect(20, 60, 280, 64, 0)
            pyxel.rectb(20, 60, 280, 64, 10)
            pyxel.rectb(22, 62, 276, 60, 7)
            t_msg = "おや……！？"
            t_sub = "相棒の様子がいつもと違う……！"
            w1 = self.app.text.measure_text_width(t_msg)
            w2 = self.app.text.measure_text_width(t_sub)
            self.app.text.draw_text(20 + (280 - w1) // 2, 72, t_msg, 10)
            self.app.text.draw_text(20 + (280 - w2) // 2, 98, t_sub, 7)

            # プルプル震え演出
            shake_amp = min(10, 2 + t // 8)
            shake_x = int(math.sin(t * 0.8) * shake_amp)
            shake_y = int(abs(math.cos(t * 0.8)) * (shake_amp // 2))

            # 進化前の相棒を描画（スケール4）
            self.app.graphics.draw_partner(
                160 + shake_x, 260 - shake_y, pid, old_stg, mood="happy", frame=self.frame, scale=4
            )

            # ヒビ割れ・汗・ビックリマーク演出
            if t > 20:
                self.app.text.draw_text(160 + shake_x + 36, 200, "！", 10)
            if t > 40:
                self.app.text.draw_text(160 + shake_x - 48, 210, "！", 9)
            if t > 55:
                self.app.text.draw_text_mini(160 + shake_x + 40, 240, "ピキッ", 7)

            self.app.text.draw_text_mini(70, 490, "光が溢れ出そうとしている……！", 12)

        elif t < 85:
            # --- フェーズ2: まばゆい光のフラッシュ点滅 ---
            flash_col = 7 if (t % 2 == 0) else 10
            pyxel.rect(0, 0, 320, 640, flash_col)
            for ang in range(0, 360, 30):
                rad = math.radians(ang + t * 5)
                ex = int(160 + math.cos(rad) * 220)
                ey = int(260 + math.sin(rad) * 220)
                pyxel.line(160, 260, ex, ey, 0 if flash_col == 7 else 7)

        else:
            # --- フェーズ3: 祝！ 新形態のお披露目 ---
            # 祝祭リボン
            pyxel.rect(30, 40, 260, 42, 10)
            pyxel.rectb(30, 40, 260, 42, 7)
            banner_text = "★ SHINKA SUCCESS!! ★"
            bw = self.app.text.measure_text_width(banner_text)
            self.app.text.draw_text(30 + (260 - bw) // 2, 52, banner_text, 0)

            # 新形態キャラクター（大きく堂々と表示、バウンス）
            b_jump = -8 if (t // 6) % 2 == 1 else 0
            self.app.graphics.draw_partner(
                160, 225 + b_jump, pid, new_stg, mood="happy", frame=self.frame, scale=4
            )

            # 周囲のカラフルパーティクル（花火風）
            for i in range(8):
                rad = math.radians(i * 45 + (self.frame * 3))
                dist = 68 + (t % 15) * 2
                px = int(160 + math.cos(rad) * dist)
                py = int(225 + math.sin(rad) * dist)
                pcol = [9, 10, 11, 12, 14][(i + t // 5) % 5]
                pyxel.circ(px, py, 2, pcol)

            # 進化完了カード (幅280, 高185, x:20, y:355)
            pyxel.rect(20, 355, 280, 185, 0)
            pyxel.rectb(20, 355, 280, 185, 10)  # 金枠
            pyxel.rectb(22, 357, 276, 181, 7)   # 白枠

            c1 = "おめでとう！ 進化したよ！！"
            w_c1 = self.app.text.measure_text_width(c1)
            self.app.text.draw_text(20 + (280 - w_c1) // 2, 368, c1, 10)

            # 旧形態 → 新形態 の矢印表示
            evolve_flow = f"{old_name}  ▶  {new_name}"
            w_flow = self.app.text.measure_text_width(evolve_flow)
            if w_flow > 240:
                w_flow_m = self.app.text.measure_text_width(evolve_flow, font_type="mini")
                self.app.text.draw_text_mini(20 + (280 - w_flow_m) // 2, 402, evolve_flow, 11)
            else:
                self.app.text.draw_text(20 + (280 - w_flow) // 2, 400, evolve_flow, 11)

            # 説明・肩書き
            w_desc = self.app.text.measure_text_width(new_desc)
            self.app.text.draw_text(20 + (280 - w_desc) // 2, 432, f"「{new_desc}」", 7)

            # メッセージ
            status_note = "新しい姿で これからも一緒に頑張ろう！"
            w_sn = self.app.text.measure_text_width(status_note, font_type="mini")
            self.app.text.draw_text_mini(20 + (280 - w_sn) // 2, 466, status_note, 7)

            # タップで部屋へ戻る案内ボタン (点滅)
            if anim["ready_to_close"]:
                btn_col = 10 if (self.frame // 8) % 2 == 0 else 7
                pyxel.rect(45, 494, 230, 32, 0)
                pyxel.rectb(45, 494, 230, 32, btn_col)
                prompt = "▶ タップしてお部屋へもどる"
                wp = self.app.text.measure_text_width(prompt)
                self.app.text.draw_text(45 + (230 - wp) // 2, 502, prompt, btn_col)

    def _draw_growth_roadmap_modal(self):
        """相棒の成長過程を一覧できる成長ロードマップ図鑑モーダル。"""
        slot_data = self.app.get_current_slot_data()
        if not slot_data:
            return
        partner = slot_data.get("partner", {})
        pid = partner.get("id", 1)
        cur_stage = partner.get("stage", 1)
        species = COMPANION_SPECIES[pid]

        # 画面暗幕
        pyxel.rect(0, 0, 320, 640, 0)

        # モーダル外枠 (x: 16, y: 35, 幅: 288, 高: 560)
        pyxel.rect(16, 35, 288, 560, 0)
        pyxel.rectb(16, 35, 288, 560, 12)  # 水色外枠
        pyxel.rectb(18, 37, 284, 556, 7)   # 白内枠

        # ヘッダー看板
        pyxel.rect(28, 48, 264, 36, 12)
        h_title = f"★ {species}の成長きろく ★"
        wh = self.app.text.measure_text_width(h_title)
        self.app.text.draw_text(28 + (264 - wh) // 2, 58, h_title, 0)

        # 4つの段階カード（y: 96, 200, 304, 408）
        stages_req = [
            (1, "第1段階: タマゴ", "最初から", 1),
            (2, "第2段階: 幼体", "Lv.5 到達", 5),
            (3, "第3段階: 成体", "Lv.15 到達", 15),
            (4, "第4段階: 究極体", "Lv.30 到達", 30),
        ]

        for idx, (stg_num, stg_label, cond_text, req_lv) in enumerate(stages_req):
            cy = 96 + idx * 104
            is_unlocked = cur_stage >= stg_num
            is_current = cur_stage == stg_num

            # カード枠
            card_border = 10 if is_current else (11 if is_unlocked else 5)
            pyxel.rect(24, cy, 272, 94, 0)
            pyxel.rectb(24, cy, 272, 94, card_border)
            if is_current:
                pyxel.rectb(26, cy + 2, 268, 90, 7)

            # 相棒グラフィック表示
            if is_unlocked:
                self.app.graphics.draw_partner(
                    54, cy + 48, pid, stg_num, mood="happy" if is_current else "normal", frame=self.frame, scale=2
                )
                name = STAGE_INFO.get(pid, [("", "")])[stg_num][0]
                desc = STAGE_INFO.get(pid, [("", "")])[stg_num][1]
            else:
                pyxel.rect(38, cy + 28, 32, 32, 5)
                self.app.text.draw_text(48, cy + 36, "？", 7)
                name = "？？？？？"
                desc = f"Lv.{req_lv} 到達で進化！"

            # テキスト情報
            self.app.text.draw_text_mini(88, cy + 12, stg_label, 6 if not is_unlocked else 12)
            self.app.text.draw_text(88, cy + 28, name, 7 if is_unlocked else 5)
            self.app.text.draw_text_mini(88, cy + 50, f"条件: {cond_text}", 10 if is_current else 6)
            self.app.text.draw_text_mini(88, cy + 68, desc, 7 if is_unlocked else 5)

            # 現在バッジ
            if is_current:
                pyxel.rect(210, cy + 8, 80, 18, 10)
                self.app.text.draw_text_mini(216, cy + 12, "★ いまここ", 0)
            elif is_unlocked:
                pyxel.rect(220, cy + 8, 70, 18, 3)
                self.app.text.draw_text_mini(226, cy + 12, "✔ 達成！", 7)

        # 最下部「タップして閉じる」
        pyxel.rect(60, 545, 200, 36, 0)
        pyxel.rectb(60, 545, 200, 36, 7)
        btn_close_text = "◀ とじる (タップ)"
        wc = self.app.text.measure_text_width(btn_close_text)
        self.app.text.draw_text(60 + (200 - wc) // 2, 555, btn_close_text, 7)

    def _draw_feeding_scene(self, partner: dict):
        """お食事演出（横向き相棒のトコトコ歩行・お皿のエサ完食・喜びジャンプ）を描画。"""
        anim = self.feeding_anim
        if not anim:
            return
        t = anim["timer"]
        pid = partner.get("id", 1)
        pstage = partner.get("stage", 1)
        food_type = anim["food_type"]

        # 1. お皿とエサの描画 (x=plate_x, y=cy)
        # bite_stage: 0=丸ごと(t < 60), 1=半分(60 <= t < 75), 2=完食(t >= 75)
        bite_stage = 0
        if t >= 75:
            bite_stage = 2
        elif t >= 60:
            bite_stage = 1
        self.app.graphics.draw_food_on_plate(anim["plate_x"], anim["cy"], food_type, bite_stage)

        # 2. 相棒の位置と状態の計算
        start_x = anim["start_x"]
        target_x = anim["target_x"]
        cy = anim["cy"]

        if t < 15:
            # 気づきフェーズ
            cur_x = start_x
            cur_y = cy
            self.app.graphics.draw_partner_side(cur_x, cur_y, pid, pstage, step_frame=0, is_eating=False, scale=3)
            # 頭上に「！」マーク (黄色10)
            self.app.text.draw_text(cur_x - 3, cur_y - 42, "!", 10)
        elif t < 60:
            # トコトコ歩行フェーズ (15..60 で 45フレームかけて start_x -> target_x)
            progress = (t - 15) / 45.0
            cur_x = int(start_x + (target_x - start_x) * progress)
            cur_y = cy
            step_frame = t - 15
            self.app.graphics.draw_partner_side(cur_x, cur_y, pid, pstage, step_frame=step_frame, is_eating=False, scale=3)
            # 足元に小さなトコトコ煙（砂煙エフェクト）
            if (t // 5) % 2 == 0:
                pyxel.pset(cur_x - 16, cur_y + 14, 7)
                pyxel.pset(cur_x - 14, cur_y + 13, 6)
        elif t < 85:
            # もぐもぐフェーズ
            cur_x = target_x
            cur_y = cy
            # 8フレーム周期で口パク/お辞儀
            eat_subframe = t - 60
            is_eating = (eat_subframe // 4) % 2 == 1
            self.app.graphics.draw_partner_side(cur_x, cur_y, pid, pstage, step_frame=0, is_eating=is_eating, scale=3)
            # もぐもぐ音符
            if is_eating:
                self.app.text.draw_text_mini(cur_x + 10, cur_y - 28, "♪", 10)
        else:
            # 85〜105: 満足・喜びジャンプフェーズ
            cur_x = target_x
            jump_sub = t - 85
            # ぴょんぴょん跳ねる
            jump_h = int(math.sin(jump_sub * 0.35) * 6)
            if jump_h < 0:
                jump_h = 0
            cur_y = cy - jump_h
            self.app.graphics.draw_partner_side(cur_x, cur_y, pid, pstage, step_frame=0, is_eating=False, scale=3)
            # ハートとEXPポップアップ
            self.app.text.draw_text_mini(cur_x - 8, cur_y - 36, "♥", 8)
            self.app.text.draw_text_mini(cur_x + 12, cur_y - 34, "♪", 10)
            self.app.text.draw_text(cur_x - 15, cur_y - 48, f"+{anim['exp_gain']} EXP", 10)

        # 「タップでスキップ」の控えめな案内（セリフ吹き出し右下）
        self.app.text.draw_text_mini(240, 106, "▶ スキップ", 5)

