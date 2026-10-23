"""Text Engine for Eiken Pre-2 App.

Handles PixelMplus font loading, word wrapping (preventing split words),
kinsoku shori (punctuation rules), and drawing text with Pyxel.
"""

import os
import pyxel

# 禁則文字（行頭に置いてはならない文字）
KINSOKU_HEAD = set("、。，．・？！?!)]}〉》」』】〕）’”,.%:;")
# 行末禁則文字（行末に置いてはならない文字）
KINSOKU_TAIL = set("([{〈《「『【〔（‘“")


class TextEngine:
    FONT_SIZE = 16

    def __init__(self, base_dir: str = "."):
        self.puf_writer = None
        self.pil_font = None
        self.fallback_font = None
        self.font_en = None
        self.font_12 = None

        # 1. 基本フォント(日本語): PyxelUniversalFont (IPA_Gothic.ttf, 16pt厳守)
        try:
            import PyxelUniversalFont as puf
            from PIL import ImageFont

            self.puf_writer = puf.Writer("IPA_Gothic.ttf")
            font_path = puf.get_data_path() + "/IPA_Gothic.ttf"
            if os.path.exists(font_path):
                self.pil_font = ImageFont.truetype(font_path, self.FONT_SIZE)
        except Exception:
            self.puf_writer = None

        fonts_dir = os.path.join(base_dir, "assets", "fonts")
        ipa_local = os.path.join(fonts_dir, "IPA_Gothic.ttf")
        noto_local = os.path.join(fonts_dir, "NotoSans-Regular.ttf")
        mplus_local = os.path.join(fonts_dir, "PixelMplus12-Regular.ttf")

        # 2. 基本フォント(日本語)用ネイティブフォールバック (IPA_Gothic.ttf 16pt厳守)
        if os.path.exists(ipa_local):
            try:
                self.fallback_font = pyxel.Font(ipa_local, self.FONT_SIZE)
            except Exception:
                self.fallback_font = None

        # 3. 基本フォント(英語): Noto Sans 16pt (英数字・記号の美麗可変幅レンダリング)
        if os.path.exists(noto_local):
            try:
                self.font_en = pyxel.Font(noto_local, self.FONT_SIZE)
            except Exception:
                self.font_en = None

        # 4. 特別フォント: PixelMplus 12pt (スロット内詳細・バッジ・補助表記専用)
        if os.path.exists(mplus_local):
            try:
                self.font_12 = pyxel.Font(mplus_local, 12)
            except Exception:
                self.font_12 = None

    def get_char_width(self, ch: str, font_type: str = "main") -> int:
        """1文字の正確なピクセル幅。"""
        if font_type == "mini":
            if self.font_12 is not None:
                return self.font_12.text_width(ch)
            return 6 if ord(ch) < 128 else 12

        if font_type == "english" and self.font_en is not None:
            return self.font_en.text_width(ch)

        # main: 日本語・英数字ともにIPAゴシック基準（等幅・垂直基準線完全一致）
        if self.fallback_font is not None:
            return self.fallback_font.text_width(ch)
        return 8 if ord(ch) < 128 else 16

    def measure_text_width(self, text: str, font_type: str = "main") -> int:
        """文字列全体のピクセル幅を正確に計算する。"""
        if font_type == "mini":
            if self.font_12 is not None:
                return self.font_12.text_width(text)
            return sum(self.get_char_width(c, "mini") for c in text)

        if font_type == "english" and self.font_en is not None:
            return self.font_en.text_width(text)

        if self.fallback_font is not None:
            return self.fallback_font.text_width(text)
        return sum(self.get_char_width(c, "main") for c in text)

    def draw_text_mini(self, x: int, y: int, text: str, color: int) -> int:
        """12pt PixelMplus フォントでテキストを描画する（バッジや補助表示用）。"""
        if self.font_12 is not None:
            pyxel.text(x, y, text, color, self.font_12)
        else:
            pyxel.text(x, y, text, color)
        return y + 12

    def wrap_text(self, text: str, max_width: int, font_type: str = "main") -> list[str]:
        """スペース区切りの単語単位で自然に改行するワードラップ処理。

        英単語が途中で切れないようにし、句読点・括弧の禁則処理（ぶら下げ・追い出し）を徹底。
        用例などのカッコブロックがはみ出る場合は、カッコの手前で美しく改行する。
        """
        lines = []
        # スマートクオート・ダッシュのASCII正規化（等幅フォールバックによるはみ出しを完全防止）
        text = (
            text.replace("’", "'")
            .replace("‘", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace("—", "-")
            .replace("–", "-")
        )
        # 改行コードで事前分割
        raw_paragraphs = text.split("\n")
        paragraphs = []

        # カッコ補足が幅を超える場合のスマート分割
        for para in raw_paragraphs:
            if self.measure_text_width(para, font_type) > max_width:
                split_done = False
                for paren in [" (", "（"]:
                    if paren in para:
                        idx = para.find(paren)
                        before = para[:idx]
                        after = para[idx:].lstrip()
                        if before and self.measure_text_width(before, font_type) <= max_width:
                            paragraphs.append(before)
                            paragraphs.append("  " + after)
                            split_done = True
                            break
                if not split_done:
                    paragraphs.append(para)
            else:
                paragraphs.append(para)

        for para in paragraphs:
            if not para:
                lines.append("")
                continue

            current_line = ""
            current_width = 0

            # 英単語・数字はアルファベット塊、スペースは個別、日本語・記号は1文字ずつ分割
            # ( ) や (1) や [word] は句読点も含めてアトミックに保護
            words = []
            i = 0
            while i < len(para):
                if para[i : i + 4] in ("( ).", "( ),", "( )?", "( )!", "( ):", "( );"):
                    words.append(para[i : i + 4])
                    i += 4
                elif para[i : i + 3] == "( )":
                    words.append("( )")
                    i += 3
                elif para[i : i + 3] in ("(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)"):
                    words.append(para[i : i + 3])
                    i += 3
                elif para[i] == "[" and "]" in para[i : i + 40]:
                    end_idx = para.find("]", i)
                    words.append(para[i : end_idx + 1])
                    i = end_idx + 1
                elif para[i].isascii() and (para[i].isalnum() or para[i] in "_-'"):
                    start = i
                    while i < len(para) and para[i].isascii() and (para[i].isalnum() or para[i] in "_-'"):
                        i += 1
                    words.append(para[start:i])
                elif para[i] == " ":
                    words.append(" ")
                    i += 1
                else:
                    words.append(para[i])
                    i += 1

            for word in words:
                word_w = self.measure_text_width(word, font_type)

                # 行頭のスペースは無視
                if not current_line and word == " ":
                    continue

                if current_width + word_w <= max_width:
                    current_line += word
                    current_width += word_w
                else:
                    # 改行が必要
                    # 行頭禁則の処理: 行頭禁則文字（句読点・！・？）が枠外にはみ出る場合、直前の1文字を巻き込んで次行へ送る
                    if word in KINSOKU_HEAD and current_line:
                        if current_line.endswith("( )"):
                            carried = "( )"
                            current_line = current_line[:-3]
                        elif current_line.endswith(")"):
                            # 括弧閉じの前の括弧開きを探す
                            open_p = current_line.rfind("(")
                            if open_p != -1 and len(current_line) - open_p <= 10:
                                carried = current_line[open_p:]
                                current_line = current_line[:open_p]
                            else:
                                carried = current_line[-1]
                                current_line = current_line[:-1]
                        else:
                            carried = current_line[-1]
                            current_line = current_line[:-1]
                        if current_line:
                            lines.append(current_line)
                        new_start = (carried + word).lstrip()
                        current_line = new_start
                        current_width = self.measure_text_width(new_start, font_type)
                        continue

                    if current_line:
                        # 行末禁則の追い出し（現行末尾が開き括弧なら次行へ送る）
                        carried = ""
                        if current_line[-1] in KINSOKU_TAIL:
                            carried = current_line[-1]
                            current_line = current_line[:-1]

                        lines.append(current_line)
                        new_start = (carried + word).lstrip()
                        current_line = new_start
                        current_width = self.measure_text_width(new_start, font_type)
                    else:
                        # 1単語だけでmax_widthを超える場合はそのまま出す
                        lines.append(word)
                        current_line = ""
                        current_width = 0

            if current_line:
                lines.append(current_line)

        return lines

    def draw_text(
        self,
        x: int,
        y: int,
        text: str,
        color: int,
        font_type: str = "main",
        max_width: int | None = None,
        line_spacing: int = 4,
    ) -> int:
        """テキストを描画する。

        max_widthが指定された場合は自動ワードラップを行う。
        返り値: 描画完了後の最下部y座標
        """
        line_h = 12 if font_type == "mini" else self.FONT_SIZE

        if max_width is not None and max_width > 0:
            lines = self.wrap_text(text, max_width, font_type)
        else:
            lines = text.split("\n")

        cur_y = y
        for line in lines:
            if line:
                if font_type == "mini":
                    self.draw_text_mini(x, cur_y, line, color)
                elif font_type == "english" and self.font_en is not None:
                    if line.isascii():
                        pyxel.text(x, cur_y, line, color, self.font_en)
                    elif self.fallback_font is not None:
                        pyxel.text(x, cur_y, line, color, self.fallback_font)
                    else:
                        pyxel.text(x, cur_y, line, color)
                elif self.fallback_font is not None:
                    pyxel.text(x, cur_y, line, color, self.fallback_font)
                elif self.puf_writer is not None:
                    self.puf_writer.draw(
                        x,
                        cur_y,
                        line,
                        font_size=self.FONT_SIZE,
                        font_color=color,
                        background_color=-1,
                    )
                else:
                    pyxel.text(x, cur_y, line, color)
            cur_y += line_h + line_spacing

        return cur_y

    def draw_text_bold(
        self,
        x: int,
        y: int,
        text: str,
        color: int,
        font_type: str = "main",
        max_width: int | None = None,
        line_spacing: int = 4,
    ) -> int:
        """白背景カードなどで文字がかすれないよう、1px重ねてくっきり太字描画する。"""
        self.draw_text(x, y, text, color, font_type, max_width, line_spacing)
        return self.draw_text(x + 1, y, text, color, font_type, max_width, line_spacing)
