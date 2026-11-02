"""Graphics and Sprite Manager for '目指せ英検準2級'

Generates and draws pixel art for:
- 5 cute animal companion species (Shiba, Cat, Rabbit, Squirrel, Penguin)
  across 4 evolution stages (Egg, Baby, Adult, Ultimate) with 2-frame animations.
- Food items (Apple, Meat).
- UI icons (Speaker, Book/CheatSheet, Star, Crown, Heart, O/X marks).
"""

import math
import os
import pyxel


class GraphicsManager:
    def __init__(self):
        self.has_title_icon = False
        self.logo_w = 304
        self.logo_h = 166
        self.logo_img = None
        self.has_logo = False
        self._load_title_logo()
        self.partner_images = {}
        self._load_partner_images()
        self._init_sprites()

    def _load_title_logo(self):
        """タイトルロゴ画像 (304x166) を Image インスタンスにロード。"""
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "assets", "images", "title_logo.png"),
            os.path.join(os.path.dirname(__file__), "assets", "images", "title_logo.png"),
            "assets/images/title_logo.png",
            "app/assets/images/title_logo.png",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    self.logo_img = pyxel.Image(self.logo_w, self.logo_h)
                    self.logo_img.load(0, 0, p)
                    self.has_logo = True
                    break
                except Exception:
                    pass

    def draw_title_logo(self, x: int = 8, y: int = 19):
        """タイトルロゴ画像を描画。"""
        if self.has_logo and self.logo_img:
            pyxel.blt(x, y, self.logo_img, 0, 0, self.logo_w, self.logo_h, 0)

    def _load_partner_images(self):
        """新キャラクター画像（48x48, 24x24）をロード。"""
        base_candidates = [
            os.path.join(os.path.dirname(__file__), "..", "assets", "images", "characters"),
            os.path.join(os.path.dirname(__file__), "assets", "images", "characters"),
            "assets/images/characters",
            "app/assets/images/characters",
        ]
        char_dir = None
        for b in base_candidates:
            if os.path.exists(b):
                char_dir = b
                break
        if not char_dir:
            return

        for pid in range(1, 6):
            for stg in range(1, 5):
                for sz in (72, 48, 24):
                    fname = f"partner_{pid}_stage_{stg}_{sz}.png"
                    fpath = os.path.join(char_dir, fname)
                    if os.path.exists(fpath):
                        try:
                            im = pyxel.Image(sz, sz)
                            im.load(0, 0, fpath)
                            self.partner_images[(pid, stg, sz)] = im
                        except Exception:
                            pass

    def _init_sprites(self):
        """Image bank 0 にスプライトデータをプログラマブルに生成・展開。"""
        # 背景透過色（11: 緑や 0: 黒など、ここでは透過色を 0 または 11 に指定して描画）
        # アイコン類の描画
        self._draw_ui_icons()
        self._draw_food_icons()

    def _draw_ui_icons(self):
        img = pyxel.images[0]

        # (0, 0) 〜 (15, 15): スピーカーアイコン（音声再生）
        # 黄色(10)と白(7)
        speaker_data = [
            "0000000000000000",
            "0000000000000000",
            "0000770000000000",
            "0007770070000000",
            "0077770007007000",
            "0777770000700700",
            "0777770000700700",
            "0777770000700700",
            "0777770000700700",
            "0077770007007000",
            "0007770070000000",
            "0000770000000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
        ]
        for y, row in enumerate(speaker_data):
            for x, c in enumerate(row):
                if c != "0":
                    img.pset(x, y, int(c, 16))

        # (16, 0) 〜 (31, 15): あんちょこ（本）アイコン
        book_data = [
            "0000000000000000",
            "0000000000000000",
            "0099999099999000",
            "0977777977777900",
            "0970007970007900",
            "0977777977777900",
            "0970007970007900",
            "0977777977777900",
            "0970007970007900",
            "0977777977777900",
            "0970007970007900",
            "0999999999999900",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
        ]
        for y, row in enumerate(book_data):
            for x, c in enumerate(row):
                if c != "0":
                    img.pset(16 + x, y, int(c, 16))

        # (32, 0) 〜 (47, 15): 星（★）アイコン (黄色 10)
        star_data = [
            "0000000000000000",
            "0000000aa0000000",
            "000000aaaa000000",
            "00000aaaaaa00000",
            "0aaaaaaaaaaaaaa0",
            "00aaaaaaaaaaaa00",
            "000aaaaaaaaaa000",
            "0000aaaaaaaa0000",
            "000aaaaaaaaaa000",
            "00aaaaaaaaaaaa00",
            "0aaaaaa00aaaaaa0",
            "0aaaa000000aaaa0",
            "0aa0000000000aa0",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
        ]
        for y, row in enumerate(star_data):
            for x, c in enumerate(row):
                if c != "0":
                    img.pset(32 + x, y, int(c, 16))

        # (48, 0) 〜 (63, 15): ハート（愛着）アイコン (赤 8, ピンク 14)
        heart_data = [
            "0000000000000000",
            "0088800000888000",
            "08eee80008eee800",
            "8eeee8008eeee800",
            "8eeeeee8eeeeee80",
            "8eeeeeeeeeeee800",
            "08eeeeeeeeee8000",
            "008eeeeeeee80000",
            "0008eeeeee800000",
            "00008eeee8000000",
            "000008ee80000000",
            "0000008800000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
        ]
        for y, row in enumerate(heart_data):
            for x, c in enumerate(row):
                if c != "0":
                    img.pset(48 + x, y, int(c, 16))

        # (64, 0) 〜 (79, 15): 王冠（クラウン）アイコン (金 10, 9)
        crown_data = [
            "0000000000000000",
            "00a0000aa0000a00",
            "0aaa00aaaa00aaa0",
            "09aa09aaaa09aa00",
            "009a09aaaa09a000",
            "009aaaa9aaaa9000",
            "0009aaaaaa900000",
            "0009aaaaaa900000",
            "009aaaaaaaa90000",
            "009aaaaaaaa90000",
            "0099999999990000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
        ]
        for y, row in enumerate(crown_data):
            for x, c in enumerate(row):
                if c != "0":
                    img.pset(64 + x, y, int(c, 16))

    def _draw_food_icons(self):
        img = pyxel.images[0]
        # (0, 16) 〜 (15, 31): リンゴ（赤 8, 緑 11）
        apple_data = [
            "0000000000000000",
            "0000000bb0000000",
            "0000000b00000000",
            "0000888088800000",
            "0008888888880000",
            "0088778888888000",
            "0888788888888800",
            "0888888888888800",
            "0888888888888800",
            "0888888888888800",
            "0088888888888000",
            "0008888888880000",
            "0000888088800000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
        ]
        for y, row in enumerate(apple_data):
            for x, c in enumerate(row):
                if c != "0":
                    img.pset(x, 16 + y, int(c, 16))

        # (16, 16) 〜 (31, 31): お肉（骨付き肉: 白 7, 肉 4, 9, 8）
        meat_data = [
            "0000000000000000",
            "0000000000000000",
            "0000044440000000",
            "0004499994400000",
            "0049988889940000",
            "0499888888994000",
            "0498877888894700",
            "0498878888894770",
            "0499888888994770",
            "0049988889940070",
            "0004499994400000",
            "0000044440000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
            "0000000000000000",
        ]
        for y, row in enumerate(meat_data):
            for x, c in enumerate(row):
                if c != "0":
                    img.pset(16 + x, 16 + y, int(c, 16))

    # =========================================================================
    # キャラクター描画ロジック（小動物5系統 × 4段階）
    # =========================================================================

    def draw_partner(
        self,
        cx: int,
        cy: int,
        partner_id: int,
        stage: int,
        mood: str = "normal",
        frame: int = 0,
        scale: int = 2,
    ):
        """相棒キャラクターを中心座標 (cx, cy) に描画。

        partner_id: 1(柴犬), 2(子猫), 3(ウサギ), 4(リス), 5(ペンギン)
        stage: 1(タマゴ), 2(幼体), 3(成体), 4(究極体)
        mood: 'normal', 'happy', 'sad'
        """
        bob = (
            1 if (frame % 30 < 15 and mood != "sad") else 0
        )  # 呼吸・待機アニメーション
        if mood == "happy":
            bob = -2 if (frame % 20 < 10) else 0  # ピョンピョン跳ねる

        y_offset = cy + bob
        target_size = 72 if scale >= 3 else (48 if scale >= 2 else 24)

        # 1. 新グラフィック画像がロードされていればテクスチャ描画
        img = self.partner_images.get((partner_id, stage, target_size))
        size = target_size
        if not img and target_size == 72:
            img = self.partner_images.get((partner_id, stage, 48))
            size = 48
        if img:
            pyxel.blt(
                cx - size // 2,
                y_offset - size // 2,
                img,
                0,
                0,
                size,
                size,
                0,
            )
            return

        # 2. フォールバック（画像がない場合）
        if stage == 1:
            # タマゴ形態（全種共通、カラーのみ少し異なる）
            self._draw_egg(cx, y_offset, partner_id, scale)
        elif partner_id == 1:
            self._draw_shiba(cx, y_offset, stage, mood, scale)
        elif partner_id == 2:
            self._draw_cat(cx, y_offset, stage, mood, scale)
        elif partner_id == 3:
            self._draw_rabbit(cx, y_offset, stage, mood, scale)
        elif partner_id == 4:
            self._draw_squirrel(cx, y_offset, stage, mood, scale)
        elif partner_id == 5:
            self._draw_penguin(cx, y_offset, stage, mood, scale)

    def draw_partner_mini(
        self, x: int, y: int, partner_id: int, stage: int, mood: str = "normal"
    ):
        """クイズ画面ヘッダー用のミニアイコン（24×24px領域）を描画。"""
        self.draw_partner(
            x + 12, y + 12, partner_id, stage, mood=mood, frame=0, scale=1
        )

    # -------------------------------------------------------------------------
    # 各キャラのドット絵描画（scale=1: 24×24, scale=2: 48×48）
    # -------------------------------------------------------------------------

    def _draw_egg(self, cx: int, cy: int, partner_id: int, scale: int):
        # 白いタマゴに、各キャラの属性色（9:橙, 14:桃, 12:水色, 4:茶, 1:紺）の斑点
        spots_color = [9, 14, 12, 4, 1][(partner_id - 1) % 5]
        s = scale
        # 外枠・白ボディ
        pyxel.elli(cx - 7 * s, cy - 9 * s, 14 * s, 18 * s, 7)
        pyxel.ellib(cx - 7 * s, cy - 9 * s, 14 * s, 18 * s, 0)
        # 斑点
        pyxel.circ(cx - 2 * s, cy - 3 * s, 2 * s, spots_color)
        pyxel.circ(cx + 3 * s, cy + 2 * s, 2 * s, spots_color)

    def _draw_shiba(
        self, cx: int, cy: int, stage: int, mood: str, scale: int
    ):
        # 柴犬: 茶色(9, 4), 白(7), 黒目(0)
        s = scale
        c_body = 9  # 茶色
        # 顔・体
        pyxel.circ(cx, cy, 8 * s, c_body)
        pyxel.circ(cx, cy + 2 * s, 5 * s, 7)  # 白い口元・胸
        # 耳（三角）
        pyxel.tri(
            cx - 6 * s,
            cy - 6 * s,
            cx - 2 * s,
            cy - 9 * s,
            cx - 7 * s,
            cy - 11 * s,
            c_body,
        )
        pyxel.tri(
            cx + 6 * s,
            cy - 6 * s,
            cx + 2 * s,
            cy - 9 * s,
            cx + 7 * s,
            cy - 11 * s,
            c_body,
        )
        # 耳の内側
        pyxel.tri(
            cx - 5 * s,
            cy - 6 * s,
            cx - 3 * s,
            cy - 8 * s,
            cx - 6 * s,
            cy - 9 * s,
            14,
        )
        pyxel.tri(
            cx + 5 * s,
            cy - 6 * s,
            cx + 3 * s,
            cy - 8 * s,
            cx + 6 * s,
            cy - 9 * s,
            14,
        )
        # 目・鼻
        self._draw_face(cx, cy, mood, s)

        # 装飾
        if stage >= 3:
            # 緑のスカーフ
            pyxel.rect(cx - 6 * s, cy + 6 * s, 12 * s, 3 * s, 11)
            pyxel.tri(
                cx, cy + 6 * s, cx + 4 * s, cy + 6 * s, cx + 2 * s, cy + 11 * s, 11
            )
        if stage >= 4:
            # 冒険家の帽子（茶色フェドーラ）
            pyxel.rect(cx - 9 * s, cy - 9 * s, 18 * s, 2 * s, 4)
            pyxel.rect(cx - 5 * s, cy - 14 * s, 10 * s, 5 * s, 4)
            pyxel.rect(cx - 5 * s, cy - 10 * s, 10 * s, 2 * s, 8)  # 赤いリボン

    def _draw_cat(self, cx: int, cy: int, stage: int, mood: str, scale: int):
        # トラネコ: 黄色(10), 白(7), ピンク耳(14)
        s = scale
        c_body = 10
        pyxel.circ(cx, cy, 7 * s, c_body)
        pyxel.circ(cx, cy + 2 * s, 4 * s, 7)
        # ピンとした耳
        pyxel.tri(
            cx - 6 * s,
            cy - 4 * s,
            cx - 2 * s,
            cy - 8 * s,
            cx - 6 * s,
            cy - 11 * s,
            c_body,
        )
        pyxel.tri(
            cx + 6 * s,
            cy - 4 * s,
            cx + 2 * s,
            cy - 8 * s,
            cx + 6 * s,
            cy - 11 * s,
            c_body,
        )
        pyxel.tri(
            cx - 5 * s,
            cy - 5 * s,
            cx - 3 * s,
            cy - 7 * s,
            cx - 5 * s,
            cy - 9 * s,
            14,
        )
        pyxel.tri(
            cx + 5 * s,
            cy - 5 * s,
            cx + 3 * s,
            cy - 7 * s,
            cx + 5 * s,
            cy - 9 * s,
            14,
        )
        # トラ縞
        pyxel.line(cx - 2 * s, cy - 6 * s, cx + 2 * s, cy - 6 * s, 9)
        pyxel.line(cx - 1 * s, cy - 4 * s, cx + 1 * s, cy - 4 * s, 9)
        # 目・鼻
        self._draw_face(cx, cy, mood, s)

        # 装飾
        if stage >= 3:
            # 赤い首元リボン
            pyxel.circ(cx, cy + 6 * s, 2 * s, 8)
            pyxel.tri(
                cx - 4 * s,
                cy + 5 * s,
                cx,
                cy + 6 * s,
                cx - 4 * s,
                cy + 8 * s,
                8,
            )
            pyxel.tri(
                cx + 4 * s,
                cy + 5 * s,
                cx,
                cy + 6 * s,
                cx + 4 * s,
                cy + 8 * s,
                8,
            )
        if stage >= 4:
            # 魔法使いケープととんがり帽子
            pyxel.tri(
                cx - 8 * s,
                cy - 7 * s,
                cx + 8 * s,
                cy - 7 * s,
                cx,
                cy - 18 * s,
                2,
            )
            pyxel.circ(cx, cy - 18 * s, 1 * s, 10)  # 星

    def _draw_rabbit(
        self, cx: int, cy: int, stage: int, mood: str, scale: int
    ):
        # ウサギ: 白(7), ピンクほっぺ(14)
        s = scale
        pyxel.circ(cx, cy, 7 * s, 7)
        # 垂れ耳
        pyxel.elli(cx - 8 * s, cy - 2 * s, 4 * s, 12 * s, 7)
        pyxel.elli(cx + 4 * s, cy - 2 * s, 4 * s, 12 * s, 7)
        pyxel.elli(cx - 7 * s, cy - 1 * s, 2 * s, 8 * s, 14)
        pyxel.elli(cx + 5 * s, cy - 1 * s, 2 * s, 8 * s, 14)
        # 目・鼻
        self._draw_face(cx, cy, mood, s)

        # 装飾
        if stage >= 3:
            # 青い羽飾り
            pyxel.elli(cx - 6 * s, cy - 6 * s, 3 * s, 7 * s, 12)
        if stage >= 4:
            # 小さなゴールドクラウン
            pyxel.tri(
                cx - 4 * s,
                cy - 7 * s,
                cx + 4 * s,
                cy - 7 * s,
                cx - 2 * s,
                cy - 11 * s,
                10,
            )
            pyxel.tri(
                cx - 1 * s,
                cy - 7 * s,
                cx + 1 * s,
                cy - 7 * s,
                cx,
                cy - 12 * s,
                10,
            )
            pyxel.tri(
                cx, cy - 7 * s, cx + 4 * s, cy - 7 * s, cx + 2 * s, cy - 11 * s, 10
            )

    def _draw_squirrel(
        self, cx: int, cy: int, stage: int, mood: str, scale: int
    ):
        # リス: 濃い茶(4, 9), ぷっくりほっぺ
        s = scale
        pyxel.circ(cx, cy, 7 * s, 9)
        # ほっぺのふくらみ
        pyxel.circ(cx - 5 * s, cy + 2 * s, 3 * s, 15)
        pyxel.circ(cx + 5 * s, cy + 2 * s, 3 * s, 15)
        # 耳
        pyxel.circ(cx - 5 * s, cy - 6 * s, 3 * s, 4)
        pyxel.circ(cx + 5 * s, cy - 6 * s, 3 * s, 4)
        # ふわふわのしっぽ（後ろ側）
        pyxel.elli(cx + 6 * s, cy - 4 * s, 8 * s, 14 * s, 4)
        pyxel.elli(cx + 7 * s, cy - 3 * s, 5 * s, 11 * s, 9)
        # 目・鼻
        self._draw_face(cx, cy, mood, s)

        # 装飾
        if stage >= 3:
            # どんぐりポシェット
            pyxel.circ(cx + 3 * s, cy + 6 * s, 3 * s, 4)
            pyxel.line(cx - 4 * s, cy + 4 * s, cx + 3 * s, cy + 6 * s, 0)
        if stage >= 4:
            # エルフ風のグリーンのケープ
            pyxel.rect(cx - 7 * s, cy + 6 * s, 14 * s, 4 * s, 3)

    def _draw_penguin(
        self, cx: int, cy: int, stage: int, mood: str, scale: int
    ):
        # ペンギンヒナ: 灰青(5), 白(7), オレンジくちばし(9)
        s = scale
        pyxel.circ(cx, cy, 8 * s, 5)
        pyxel.circ(cx, cy + 2 * s, 6 * s, 7)  # 白いおなか
        # 小さなパタパタ羽
        pyxel.elli(cx - 8 * s, cy + 1 * s, 3 * s, 6 * s, 5)
        pyxel.elli(cx + 5 * s, cy + 1 * s, 3 * s, 6 * s, 5)
        # 目・くちばし
        if mood == "sad":
            pyxel.line(
                cx - 4 * s, cy - 1 * s, cx - 2 * s, cy + 1 * s, 0
            )  # しょんぼり目
            pyxel.line(cx + 4 * s, cy - 1 * s, cx + 2 * s, cy + 1 * s, 0)
        elif mood == "happy":
            pyxel.line(
                cx - 4 * s, cy + 1 * s, cx - 2 * s, cy - 1 * s, 0
            )  # ニッコリ目
            pyxel.line(cx - 2 * s, cy - 1 * s, cx, cy + 1 * s, 0)
            pyxel.line(cx + 2 * s, cy - 1 * s, cx + 4 * s, cy + 1 * s, 0)
        else:
            pyxel.circ(cx - 3 * s, cy, 1 * s, 0)  # つぶらな瞳
            pyxel.circ(cx + 3 * s, cy, 1 * s, 0)
        # オレンジのくちばし
        pyxel.tri(
            cx - 2 * s, cy + 2 * s, cx + 2 * s, cy + 2 * s, cx, cy + 4 * s, 9
        )

        # 装飾
        if stage >= 3:
            # キャプテンハット（濃紺に金ライン）
            pyxel.rect(cx - 6 * s, cy - 9 * s, 12 * s, 4 * s, 1)
            pyxel.rect(cx - 6 * s, cy - 6 * s, 12 * s, 1 * s, 10)
        if stage >= 4:
            # 氷のティアラ
            pyxel.tri(
                cx - 4 * s, cy - 7 * s, cx, cy - 12 * s, cx + 4 * s, cy - 7 * s, 12
            )
            pyxel.circ(cx, cy - 12 * s, 1 * s, 7)

    def _draw_face(self, cx: int, cy: int, mood: str, s: int):
        """目と鼻の共通描画。"""
        if mood == "happy":
            # にっこり目（＾ ＾）
            pyxel.line(cx - 4 * s, cy - 1 * s, cx - 2 * s, cy - 3 * s, 0)
            pyxel.line(cx - 2 * s, cy - 3 * s, cx, cy - 1 * s, 0)
            pyxel.line(cx + 2 * s, cy - 3 * s, cx + 4 * s, cy - 1 * s, 0)
            # ピンクほっぺ
            pyxel.circ(cx - 5 * s, cy + 1 * s, 1 * s, 14)
            pyxel.circ(cx + 5 * s, cy + 1 * s, 1 * s, 14)
        elif mood == "sad":
            # 泣き目・しょんぼり
            pyxel.line(cx - 4 * s, cy - 3 * s, cx - 2 * s, cy - 1 * s, 0)
            pyxel.line(cx + 4 * s, cy - 3 * s, cx + 2 * s, cy - 1 * s, 0)
            pyxel.circ(cx - 4 * s, cy + 1 * s, 1 * s, 12)  # 涙
        else:
            # つぶらな黒目
            pyxel.circ(cx - 3 * s, cy - 1 * s, 1 * s, 0)
            pyxel.circ(cx + 3 * s, cy - 1 * s, 1 * s, 0)
        # 小さな黒鼻
        pyxel.pset(cx, cy + 2 * s, 0)

    # =========================================================================
    # お食事アニメーション用（お皿＋エサ ＆ 横向き歩行キャラクター）
    # =========================================================================

    def draw_food_on_plate(
        self, cx: int, cy: int, food_type: str, bite_stage: int = 0
    ):
        """お皿に乗ったエサを描画。
        food_type: 'apple', 'meat', 'golden_apple'
        bite_stage: 0=丸ごと, 1=半分・かじりかけ, 2=完食
        """
        # 1. ランチョンマット（テーブル敷物）
        pyxel.rect(cx - 26, cy + 9, 52, 4, 4)   # ウッドブラウン
        pyxel.rect(cx - 24, cy + 10, 48, 2, 9)  # 木目ハイライト

        # 2. 陶器プレート（白皿＋グレーの陰影）
        pyxel.elli(cx - 20, cy + 3, 40, 14, 7)   # 皿外形（白）
        pyxel.ellib(cx - 20, cy + 3, 40, 14, 13) # グレー縁
        pyxel.elli(cx - 15, cy + 5, 30, 8, 6)    # 内側のくぼみ影
        pyxel.elli(cx - 15, cy + 5, 30, 7, 7)    # 内側の白

        # 3. エサの描画
        if food_type == "apple":
            if bite_stage == 0:
                # 丸ごとリンゴ
                pyxel.circ(cx, cy - 2, 7, 8)
                pyxel.pset(cx - 2, cy - 5, 7)  # ハイライト
                pyxel.pset(cx - 1, cy - 6, 7)
                pyxel.line(cx, cy - 8, cx + 1, cy - 11, 4)  # ヘタ
                pyxel.pset(cx + 2, cy - 10, 11)             # 葉っぱ
            elif bite_stage == 1:
                # 半分かじりかけ
                pyxel.elli(cx - 7, cy - 8, 8, 12, 8)
                pyxel.line(cx - 2, cy - 7, cx - 2, cy + 3, 10)  # 果肉
                pyxel.line(cx - 4, cy - 8, cx - 3, cy - 11, 4)  # ヘタ
                pyxel.pset(cx + 3, cy - 3, 8)  # カケラ
                pyxel.pset(cx + 6, cy, 8)
            else:
                # 完食（芯と小さなタネ）
                pyxel.line(cx, cy - 2, cx + 1, cy + 4, 4)
                pyxel.pset(cx - 2, cy + 2, 0)
                pyxel.pset(cx + 2, cy + 3, 0)

        elif food_type == "meat":
            if bite_stage == 0:
                # 丸ごと骨付き肉
                pyxel.line(cx - 14, cy - 2, cx + 14, cy - 2, 7)
                pyxel.circ(cx - 14, cy - 4, 2, 7)
                pyxel.circ(cx - 14, cy, 2, 7)
                pyxel.circ(cx + 14, cy - 4, 2, 7)
                pyxel.circ(cx + 14, cy, 2, 7)
                pyxel.elli(cx - 9, cy - 8, 18, 12, 4)
                pyxel.elli(cx - 8, cy - 7, 16, 10, 9)
                pyxel.line(cx - 4, cy - 4, cx + 4, cy - 4, 8)  # 焼き目
            elif bite_stage == 1:
                # 半分かじられた肉
                pyxel.line(cx - 14, cy - 2, cx + 14, cy - 2, 7)
                pyxel.circ(cx - 14, cy - 4, 2, 7)
                pyxel.circ(cx - 14, cy, 2, 7)
                pyxel.circ(cx + 14, cy - 4, 2, 7)
                pyxel.circ(cx + 14, cy, 2, 7)
                pyxel.elli(cx - 9, cy - 7, 10, 10, 9)
                pyxel.pset(cx + 4, cy - 1, 9)  # カケラ
                pyxel.pset(cx + 7, cy + 1, 8)
            else:
                # 完食（ツルツルの骨だけ）
                pyxel.line(cx - 14, cy + 2, cx + 14, cy + 2, 7)
                pyxel.circ(cx - 14, cy, 2, 7)
                pyxel.circ(cx - 14, cy + 4, 2, 7)
                pyxel.circ(cx + 14, cy, 2, 7)
                pyxel.circ(cx + 14, cy + 4, 2, 7)

        elif food_type == "golden_apple":
            if bite_stage == 0:
                # 黄金のリンゴ（輝き付き）
                pyxel.circ(cx, cy - 2, 7, 10)
                pyxel.pset(cx - 2, cy - 5, 7)
                pyxel.line(cx, cy - 8, cx + 1, cy - 11, 9)
                pyxel.pset(cx + 2, cy - 10, 10)
                # キラキラ粒子
                pyxel.pset(cx - 8, cy - 8, 7)
                pyxel.pset(cx + 9, cy - 6, 10)
                pyxel.pset(cx - 6, cy + 2, 10)
            elif bite_stage == 1:
                # 半分かじられた金リンゴ
                pyxel.elli(cx - 7, cy - 8, 8, 12, 10)
                pyxel.line(cx - 2, cy - 7, cx - 2, cy + 3, 9)
                pyxel.line(cx - 4, cy - 8, cx - 3, cy - 11, 9)
                pyxel.pset(cx + 3, cy - 3, 10)
                pyxel.pset(cx + 6, cy, 7)
            else:
                # 完食（ふわっと舞う金色の星屑）
                pyxel.pset(cx - 4, cy - 2, 10)
                pyxel.pset(cx + 5, cy - 5, 7)
                pyxel.pset(cx, cy - 8, 10)
                pyxel.pset(cx + 2, cy + 1, 9)

    def draw_partner_side(
        self,
        cx: int,
        cy: int,
        partner_id: int,
        stage: int,
        step_frame: int = 0,
        is_eating: bool = False,
        scale: int = 3,
    ):
        """右向き（横向き）の相棒キャラクターを描画。歩行トコトコ＆もぐもぐに対応。"""
        s = scale
        if stage == 1:
            self._draw_egg_side(cx, cy, partner_id, step_frame, is_eating, s)
        elif partner_id == 1:
            self._draw_shiba_side(cx, cy, stage, step_frame, is_eating, s)
        elif partner_id == 2:
            self._draw_cat_side(cx, cy, stage, step_frame, is_eating, s)
        elif partner_id == 3:
            self._draw_rabbit_side(cx, cy, stage, step_frame, is_eating, s)
        elif partner_id == 4:
            self._draw_squirrel_side(cx, cy, stage, step_frame, is_eating, s)
        elif partner_id == 5:
            self._draw_penguin_side(cx, cy, stage, step_frame, is_eating, s)

    def _draw_egg_side(self, cx, cy, partner_id, step_frame, is_eating, s):
        # タマゴ: 歩行時はピョンピョン跳ね、食事時はコツコツお辞儀
        spots_color = [9, 14, 12, 4, 1][(partner_id - 1) % 5]
        if is_eating:
            pitch = int(math.sin(step_frame * 0.5) * 3 * s)
            bounce = 0
        else:
            bounce = -int(abs(math.sin(step_frame * 0.25)) * 6)
            pitch = int(math.sin(step_frame * 0.25) * 2 * s)

        # 白いタマゴ
        pyxel.elli(cx - 7 * s + pitch, cy - 9 * s + bounce, 14 * s, 18 * s, 7)
        pyxel.ellib(cx - 7 * s + pitch, cy - 9 * s + bounce, 14 * s, 18 * s, 0)
        # 斑点
        pyxel.circ(cx - 1 * s + pitch, cy - 3 * s + bounce, 2 * s, spots_color)
        pyxel.circ(cx + 4 * s + pitch, cy + 2 * s + bounce, 2 * s, spots_color)

    def _draw_shiba_side(self, cx, cy, stage, step_frame, is_eating, s):
        c_body = 9
        if is_eating:
            pitch = 2 * s if (step_frame // 4) % 2 == 1 else 0
            bounce = 0
            leg_f = 0
            leg_b = 0
        else:
            pitch = 0
            bounce = -2 if (step_frame // 4) % 2 == 1 else 0
            leg_f = int(math.sin(step_frame * 0.4) * 3 * s)
            leg_b = -leg_f

        # 1. 後ろ足・前足（奥側）
        pyxel.rect(cx - 3 * s - leg_b, cy + 3 * s + bounce, 2 * s, 4 * s, 4)
        pyxel.rect(cx + 4 * s - leg_f, cy + 3 * s + bounce, 2 * s, 4 * s, 4)

        # 2. 巻き尾（左側・お尻）
        pyxel.circ(cx - 6 * s, cy - 4 * s + bounce, 2 * s, c_body)
        pyxel.circ(cx - 7 * s, cy - 6 * s + bounce, 1 * s, 7)

        # 3. 胴体（横長の丸み）
        pyxel.elli(cx - 6 * s, cy - 3 * s + bounce, 12 * s, 8 * s, c_body)
        pyxel.elli(cx - 3 * s, cy + 1 * s + bounce, 8 * s, 4 * s, 7)  # 白いお腹

        # 4. 手前足（前足・後ろ足）
        pyxel.rect(cx - 4 * s + leg_b, cy + 4 * s + bounce, 2 * s, 4 * s, c_body)
        pyxel.rect(cx - 4 * s + leg_b, cy + 7 * s + bounce, 2 * s, 1 * s, 7)  # 白足先
        pyxel.rect(cx + 3 * s + leg_f, cy + 4 * s + bounce, 2 * s, 4 * s, c_body)
        pyxel.rect(cx + 3 * s + leg_f, cy + 7 * s + bounce, 2 * s, 1 * s, 7)  # 白足先

        # 5. 頭部（右寄り）
        hx = cx + 4 * s
        hy = cy - 6 * s + bounce + pitch
        pyxel.circ(hx, hy, 6 * s, c_body)

        # マズル（白い口元＋黒鼻）
        pyxel.elli(hx + 3 * s, hy + 1 * s, 5 * s, 4 * s, 7)
        pyxel.pset(hx + 6 * s, hy, 0)
        if is_eating and (step_frame // 4) % 2 == 1:
            pyxel.pset(hx + 5 * s, hy + 2 * s, 8)  # パクッと開いた口

        # 耳（三角）
        pyxel.tri(hx - 3 * s, hy - 4 * s, hx - 1 * s, hy - 9 * s, hx - 5 * s, hy - 9 * s, c_body)
        pyxel.tri(hx - 2 * s, hy - 5 * s, hx - 1 * s, hy - 8 * s, hx - 4 * s, hy - 8 * s, 14)

        # 目とほっぺ
        if is_eating:
            # にっこり目
            pyxel.line(hx + 1 * s, hy - 2 * s, hx + 3 * s, hy - 3 * s, 0)
            pyxel.line(hx + 3 * s, hy - 3 * s, hx + 4 * s, hy - 1 * s, 0)
        else:
            pyxel.circ(hx + 2 * s, hy - 2 * s, 1 * s, 0)
        pyxel.circ(hx + 1 * s, hy + 1 * s, 1 * s, 14)  # ほっぺ

        # 装飾
        if stage >= 3:
            # スカーフ
            pyxel.rect(hx - 3 * s, hy + 4 * s, 4 * s, 2 * s, 11)
            pyxel.tri(hx - 3 * s, hy + 5 * s, hx - 6 * s, hy + 7 * s, hx - 3 * s, hy + 8 * s, 11)
        if stage >= 4:
            # 探検帽子
            pyxel.rect(hx - 5 * s, hy - 9 * s, 11 * s, 2 * s, 4)
            pyxel.rect(hx - 3 * s, hy - 13 * s, 7 * s, 4 * s, 4)
            pyxel.rect(hx - 3 * s, hy - 10 * s, 7 * s, 1 * s, 8)

    def _draw_cat_side(self, cx, cy, stage, step_frame, is_eating, s):
        c_body = 10
        if is_eating:
            pitch = 2 * s if (step_frame // 4) % 2 == 1 else 0
            bounce = 0
            leg_f = 0
            leg_b = 0
        else:
            pitch = 0
            bounce = -2 if (step_frame // 4) % 2 == 1 else 0
            leg_f = int(math.sin(step_frame * 0.4) * 3 * s)
            leg_b = -leg_f

        # 1. 奥足
        pyxel.rect(cx - 3 * s - leg_b, cy + 3 * s + bounce, 2 * s, 4 * s, 9)
        pyxel.rect(cx + 4 * s - leg_f, cy + 3 * s + bounce, 2 * s, 4 * s, 9)

        # 2. ピンと立った猫しっぽ（左上へ曲がる）
        tail_wobble = int(math.sin(step_frame * 0.3) * 2 * s)
        pyxel.line(cx - 5 * s, cy + bounce, cx - 7 * s, cy - 6 * s + bounce + tail_wobble, c_body)
        pyxel.line(cx - 7 * s, cy - 6 * s + bounce + tail_wobble, cx - 5 * s, cy - 8 * s + bounce + tail_wobble, c_body)

        # 3. 胴体
        pyxel.elli(cx - 5 * s, cy - 3 * s + bounce, 11 * s, 7 * s, c_body)
        pyxel.line(cx - 2 * s, cy - 6 * s + bounce, cx + 1 * s, cy - 6 * s + bounce, 9)  # トラ縞
        pyxel.elli(cx - 2 * s, cy + 1 * s + bounce, 7 * s, 3 * s, 7)  # 白腹

        # 4. 手前足
        pyxel.rect(cx - 4 * s + leg_b, cy + 3 * s + bounce, 2 * s, 4 * s, c_body)
        pyxel.rect(cx + 3 * s + leg_f, cy + 3 * s + bounce, 2 * s, 4 * s, c_body)

        # 5. 頭部
        hx = cx + 4 * s
        hy = cy - 5 * s + bounce + pitch
        pyxel.circ(hx, hy, 5 * s, c_body)

        # 耳（ピンとした三角）
        pyxel.tri(hx - 2 * s, hy - 4 * s, hx, hy - 8 * s, hx - 4 * s, hy - 8 * s, c_body)
        pyxel.tri(hx - 1 * s, hy - 5 * s, hx, hy - 7 * s, hx - 3 * s, hy - 7 * s, 14)

        # マズルとヒゲ
        pyxel.circ(hx + 3 * s, hy + 1 * s, 2 * s, 7)
        pyxel.pset(hx + 4 * s, hy, 14)  # ピンク鼻
        pyxel.line(hx + 4 * s, hy, hx + 7 * s, hy - 1 * s, 0)  # ヒゲ
        pyxel.line(hx + 4 * s, hy + 1 * s, hx + 7 * s, hy + 2 * s, 0)
        if is_eating and (step_frame // 4) % 2 == 1:
            pyxel.pset(hx + 4 * s, hy + 2 * s, 8)

        # 目・ほっぺ
        if is_eating:
            pyxel.line(hx + 1 * s, hy - 2 * s, hx + 3 * s, hy - 2 * s, 0)
        else:
            pyxel.circ(hx + 2 * s, hy - 2 * s, 1 * s, 0)
        pyxel.circ(hx + 1 * s, hy + 1 * s, 1 * s, 14)

        # 装飾
        if stage >= 3:
            pyxel.circ(hx - 1 * s, hy + 4 * s, 1 * s, 8)
            pyxel.pset(hx - 1 * s, hy + 5 * s, 10)  # 鈴
        if stage >= 4:
            pyxel.rect(hx - 3 * s, hy - 8 * s, 8 * s, 4 * s, 8)
            pyxel.pset(hx - 3 * s, hy - 9 * s, 7)

    def _draw_rabbit_side(self, cx, cy, stage, step_frame, is_eating, s):
        if is_eating:
            pitch = 2 * s if (step_frame // 4) % 2 == 1 else 0
            hop = 0
        else:
            pitch = 0
            hop = -int(abs(math.sin(step_frame * 0.3)) * 8)

        # 1. まるいポンポンしっぽ（左お尻）
        pyxel.circ(cx - 7 * s, cy - 1 * s + hop, 2 * s, 7)

        # 2. 胴体（白いおもち型）
        pyxel.elli(cx - 5 * s, cy - 3 * s + hop, 11 * s, 8 * s, 7)

        # 3. 足（跳ね足）
        pyxel.elli(cx - 4 * s, cy + 3 * s + hop, 4 * s, 3 * s, 7)
        pyxel.elli(cx + 3 * s, cy + 3 * s + hop, 3 * s, 3 * s, 7)

        # 4. 頭部
        hx = cx + 4 * s
        hy = cy - 5 * s + hop + pitch
        pyxel.circ(hx, hy, 5 * s, 7)

        # 長い垂れ耳（後ろになびく）
        pyxel.elli(hx - 4 * s, hy - 4 * s, 3 * s, 9 * s, 7)
        pyxel.elli(hx - 4 * s, hy - 3 * s, 2 * s, 6 * s, 14)

        # お口（もぐもぐ時は×がパクパク）
        pyxel.pset(hx + 4 * s, hy + 1 * s, 14)  # 鼻
        if is_eating and (step_frame // 4) % 2 == 1:
            pyxel.pset(hx + 4 * s, hy + 2 * s, 8)

        # 目・ほっぺ
        if is_eating:
            pyxel.line(hx + 1 * s, hy - 2 * s, hx + 3 * s, hy - 2 * s, 0)
        else:
            pyxel.circ(hx + 2 * s, hy - 2 * s, 1 * s, 0)
        pyxel.circ(hx + 1 * s, hy + 1 * s, 1 * s, 14)

        # 装飾
        if stage >= 3:
            pyxel.pset(hx - 1 * s, hy + 4 * s, 12)  # 蝶ネクタイ
        if stage >= 4:
            # 近衛兵の黒い高帽子
            pyxel.rect(hx - 3 * s, hy - 14 * s, 6 * s, 9 * s, 0)
            pyxel.rect(hx - 2 * s, hy - 6 * s, 5 * s, 1 * s, 10)

    def _draw_squirrel_side(self, cx, cy, stage, step_frame, is_eating, s):
        c_body = 9
        if is_eating:
            pitch = 2 * s if (step_frame // 4) % 2 == 1 else 0
            bounce = 0
            leg_w = 0
        else:
            pitch = 0
            bounce = -2 if (step_frame // 3) % 2 == 1 else 0
            leg_w = int(math.sin(step_frame * 0.6) * 3 * s)

        # 1. 特大のモフモフ縞しっぽ（背中を覆う大きなカーブ）
        tail_bob = int(math.sin(step_frame * 0.4) * 2 * s)
        pyxel.elli(cx - 9 * s, cy - 8 * s + bounce + tail_bob, 8 * s, 13 * s, 4)
        pyxel.elli(cx - 8 * s, cy - 7 * s + bounce + tail_bob, 5 * s, 10 * s, c_body)
        pyxel.elli(cx - 7 * s, cy - 6 * s + bounce + tail_bob, 3 * s, 7 * s, 15)  # 白縞

        # 2. 胴体（ちょこんと直立）
        pyxel.elli(cx - 4 * s, cy - 2 * s + bounce, 9 * s, 8 * s, c_body)
        pyxel.elli(cx - 2 * s, cy + 1 * s + bounce, 6 * s, 4 * s, 15)  # 白腹

        # 3. 足（小股でタタタタッ）
        pyxel.rect(cx - 3 * s - leg_w, cy + 4 * s + bounce, 2 * s, 3 * s, 4)
        pyxel.rect(cx + 2 * s + leg_w, cy + 4 * s + bounce, 2 * s, 3 * s, 4)

        # 4. 頭部
        hx = cx + 3 * s
        hy = cy - 6 * s + bounce + pitch
        pyxel.circ(hx, hy, 5 * s, c_body)

        # ぷっくりほっぺ
        pyxel.circ(hx + 2 * s, hy + 2 * s, 2 * s, 15)
        pyxel.pset(hx + 4 * s, hy + 1 * s, 0)  # 鼻

        # 耳（丸耳）
        pyxel.circ(hx - 2 * s, hy - 5 * s, 2 * s, 4)

        # 手（胸元でエサをちょこん）
        pyxel.circ(hx + 2 * s, hy + 4 * s, 1 * s, 15)

        # 目
        if is_eating:
            pyxel.line(hx + 1 * s, hy - 2 * s, hx + 3 * s, hy - 2 * s, 0)
        else:
            pyxel.circ(hx + 2 * s, hy - 2 * s, 1 * s, 0)

        # 装飾
        if stage >= 3:
            pyxel.circ(cx, cy + 2 * s + bounce, 2 * s, 4)  # ポシェット
        if stage >= 4:
            pyxel.rect(hx - 4 * s, hy - 9 * s, 8 * s, 2 * s, 0)  # 博士帽
            pyxel.pset(hx - 4 * s, hy - 8 * s, 10)

    def _draw_penguin_side(self, cx, cy, stage, step_frame, is_eating, s):
        c_body = 5
        if is_eating:
            pitch = 2 * s if (step_frame // 4) % 2 == 1 else 0
            waddle = 0
            flipper_ang = 1 * s
        else:
            pitch = 0
            waddle = int(math.sin(step_frame * 0.35) * 2 * s)
            flipper_ang = int(abs(math.sin(step_frame * 0.35)) * 3 * s)

        # 1. 胴体（タマゴ型）
        pyxel.elli(cx - 4 * s, cy - 4 * s + waddle, 9 * s, 12 * s, c_body)
        pyxel.elli(cx, cy - 2 * s + waddle, 5 * s, 9 * s, 7)  # 白いおなか

        # 2. 水かき足（オレンジ）
        leg_step = int(math.sin(step_frame * 0.35) * 2 * s) if not is_eating else 0
        pyxel.rect(cx - 2 * s - leg_step, cy + 6 * s + waddle, 3 * s, 2 * s, 9)
        pyxel.rect(cx + 2 * s + leg_step, cy + 6 * s + waddle, 3 * s, 2 * s, 9)

        # 3. 頭部＋くちばし
        hx = cx + 1 * s
        hy = cy - 3 * s + waddle + pitch
        # 頭部（青い丸）
        pyxel.circ(hx, hy, 4 * s, c_body)
        # 白い顔・おなかの上部
        pyxel.elli(hx, hy - 1 * s, 3 * s, 4 * s, 7)

        # オレンジのくちばし（右に突き出る）
        pyxel.tri(hx + 2 * s, hy, hx + 6 * s, hy + 1 * s, hx + 2 * s, hy + 2 * s, 9)
        if is_eating and (step_frame // 4) % 2 == 1:
            pyxel.pset(hx + 3 * s, hy + 1 * s, 0)

        # 目
        if is_eating:
            pyxel.line(hx, hy - 1 * s, hx + 2 * s, hy - 1 * s, 0)
        else:
            pyxel.circ(hx + 1 * s, hy - 1 * s, 1 * s, 0)

        # 4. フリッパー（翼・パタパタ）
        pyxel.line(cx - 1 * s, cy - 1 * s + waddle, cx - 4 * s, cy + 2 * s + waddle + flipper_ang, c_body)
        pyxel.line(cx, cy - 1 * s + waddle, cx - 3 * s, cy + 3 * s + waddle + flipper_ang, c_body)

        # 装飾
        if stage >= 3:
            pyxel.rect(hx - 3 * s, hy - 5 * s, 7 * s, 2 * s, 1)
            pyxel.rect(hx - 3 * s, hy - 3 * s, 7 * s, 1 * s, 10)
        if stage >= 4:
            pyxel.rect(hx - 3 * s, hy - 5 * s, 7 * s, 2 * s, 4)  # 飛行帽
            pyxel.circ(hx + 1 * s, hy - 4 * s, 1 * s, 12)        # ゴーグル

    def init_title_icon(self, project_root: str):
        """タイトル用アプリアイコンをイメージバンク1にロード。"""
        candidates = [
            os.path.join(project_root, "assets", "images", "title_icon_72.png"),
            os.path.join(project_root, "app", "assets", "images", "title_icon_72.png"),
            "assets/images/title_icon_72.png",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    pyxel.images[1].load(0, 0, path)
                    self.has_title_icon = True
                    break
                except Exception:
                    pass

    def draw_title_banner(self, x: int, y: int, text_engine):
        """タイトル看板（アイコン＋タイトル文字）を描画。"""
        # 看板枠（黒背景＋白外枠＋白内枠）
        pyxel.rect(x, y, 288, 88, 0)
        pyxel.rectb(x, y, 288, 88, 7)
        pyxel.rectb(x + 2, y + 2, 284, 84, 7)

        # アプリアイコン描画（72x72）
        if self.has_title_icon:
            pyxel.blt(x + 8, y + 8, 1, 0, 0, 72, 72, 0)
        else:
            # フォールバック: 柴犬のドット絵アイコン
            pyxel.rect(x + 8, y + 8, 72, 72, 1)
            pyxel.rectb(x + 8, y + 8, 72, 72, 7)
            self.draw_partner(x + 44, y + 44, 1, 2, mood="happy", scale=2)

        # タイトルテキスト（右側: 落ち着いた白文字に統一）
        text_engine.draw_text(x + 90, y + 12, "目指せ英検準２級", 7)
        text_engine.draw_text(x + 90, y + 34, "小動物と学ぶ", 7)
        text_engine.draw_text(x + 90, y + 56, "合格育成ゲーム！", 7)

    def draw_title_mascots(self, x: int, y: int, text_engine):
        """タイトル画面下部の相棒集合ステージを描画。"""
        # ステージ枠（黒下地＋白外枠＋暗灰内枠）
        pyxel.rect(x, y, 288, 195, 0)
        pyxel.rectb(x, y, 288, 195, 7)
        pyxel.rectb(x + 2, y + 2, 284, 191, 5)

        # ステージ見出しリボン（黒背景＋白枠＋白文字でくっきり視認）
        pyxel.rect(x + 44, y - 10, 200, 20, 0)
        pyxel.rectb(x + 44, y - 10, 200, 20, 7)
        ribbon_str = "５ひきの相棒たち"
        rw = text_engine.measure_text_width(ribbon_str)
        text_engine.draw_text(x + 44 + (200 - rw) // 2, y - 8, ribbon_str, 7)

        # 芝生グラウンドライン
        pyxel.rect(x + 6, y + 110, 276, 4, 3)   # 深緑
        pyxel.rect(x + 6, y + 112, 276, 2, 11)  # 明緑

        # 5匹の相棒たちを横並びで描画 (scale=2)
        partners = [
            (1, x + 32),
            (2, x + 88),
            (3, x + 144),
            (4, x + 200),
            (5, x + 256),
        ]
        for pid, cx in partners:
            self.draw_partner(cx, y + 75, pid, stage=2, mood="happy", scale=2)

        # ごはんアイテム（リンゴとお肉）
        pyxel.blt(x + 69, y + 119, 0, 0, 16, 16, 16, 0)
        pyxel.blt(x + 204, y + 119, 0, 16, 16, 16, 16, 0)

        # キャッチコピーメッセージ（育成システムの役割を明記）
        cp1 = "問題を解いてエサをあげよう！"
        w1 = text_engine.measure_text_width(cp1)
        text_engine.draw_text((320 - w1) // 2, y + 140, cp1, 7)

        cp2 = "相棒がどんどん進化するよ！"
        w2 = text_engine.measure_text_width(cp2)
        text_engine.draw_text((320 - w2) // 2, y + 165, cp2, 7)

