"""Main Entry Point for '目指せ英検準2級'

Initializes Pyxel at 320x640 resolution (1:2 ratio),
loads PixelMplus fonts, quiz data, audio, storage, and graphics,
and manages scene transitions.
"""

import json
import os
import sys

# 自作モジュールのインポートパス設定
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import pyxel
from audio_engine import AudioEngine
from graphics import GraphicsManager
from storage import StorageManager
from text_engine import TextEngine

from scenes.scene_data_manage import SceneDataManage
from scenes.scene_home import SceneHome
from scenes.scene_map import SceneMap
from scenes.scene_quiz import SceneQuiz
from scenes.scene_result import SceneResult
from scenes.scene_review import SceneReview
from scenes.scene_title import SceneTitle


class EikenApp:
    def __init__(self):
        # 画面解像度 320 × 640 px (比率 1:2, 現代スマホ縦画面最適化)
        pyxel.init(320, 640, title="目指せ英検準2級", fps=30)
        pyxel.mouse(False)

        # 基盤エンジンの初期化（Webパッケージ内・ローカル実行の両対応）
        candidates = [
            os.path.abspath(src_dir),
            os.path.abspath(os.path.join(src_dir, "..")),
            os.path.abspath("."),
        ]
        project_root = next(
            (c for c in candidates if os.path.exists(os.path.join(c, "data", "quiz_data.json"))),
            os.path.abspath(src_dir),
        )
        self.project_root = project_root
        self.text = TextEngine(base_dir=project_root)
        self.storage = StorageManager(
            data_dir=os.path.join(project_root, "data")
        )
        self.audio = AudioEngine(
            voices_dir=os.path.join(project_root, "assets", "voices")
        )
        self.graphics = GraphicsManager()
        self.graphics.init_title_icon(project_root)

        # クイズデータのロード
        quiz_data_path = os.path.join(project_root, "data", "quiz_data.json")
        with open(quiz_data_path, "r", encoding="utf-8") as f:
            self.quiz_data = json.load(f)

        # DUO 3.0 クイズデータのロード
        duo_data_path = os.path.join(project_root, "data", "duo_data.json")
        if os.path.exists(duo_data_path):
            try:
                with open(duo_data_path, "r", encoding="utf-8") as f:
                    self.duo_data = json.load(f)
            except Exception:
                self.duo_data = {"sections": [], "total_questions": 0}
        else:
            self.duo_data = {"sections": [], "total_questions": 0}

        # 状態管理
        self.current_slot = 1

        # シーンの初期化
        self.scenes = {
            "title": SceneTitle(self),
            "home": SceneHome(self),
            "map": SceneMap(self),
            "quiz": SceneQuiz(self),
            "result": SceneResult(self),
            "review": SceneReview(self),
            "data_manage": SceneDataManage(self),
        }
        self.current_scene_name = "title"

    def get_current_slot_data(self) -> dict | None:
        return self.storage.slots.get(self.current_slot)

    def change_scene(self, scene_name: str):
        if scene_name in self.scenes:
            self.current_scene_name = scene_name
            scene_obj = self.scenes[scene_name]
            if hasattr(scene_obj, "on_enter"):
                scene_obj.on_enter()

    def start_quiz(self, lesson: dict):
        quiz_scene: SceneQuiz = self.scenes["quiz"]
        quiz_scene.start_quiz(lesson)
        self.change_scene("quiz")

    def start_duo_quiz(self, section: dict):
        quiz_scene: SceneQuiz = self.scenes["quiz"]
        quiz_scene.start_duo_quiz(section)
        self.change_scene("quiz")

    def start_daily_duo_quiz(self):
        quiz_scene: SceneQuiz = self.scenes["quiz"]
        quiz_scene.start_daily_duo_quiz()
        self.change_scene("quiz")

    def finish_quiz(
        self,
        lesson: dict,
        correct_count: int,
        total_questions: int,
        total_exp: int,
        quiz_mode: str = "eiken",
    ):
        result_scene: SceneResult = self.scenes["result"]
        result_scene.set_result(
            lesson,
            correct_count,
            total_questions,
            total_exp,
            quiz_mode=quiz_mode,
        )
        self.change_scene("result")

    def update(self):
        cur_scene = self.scenes.get(self.current_scene_name)
        if cur_scene:
            cur_scene.update()

    def draw(self):
        cur_scene = self.scenes.get(self.current_scene_name)
        if cur_scene:
            cur_scene.draw()


def main():
    app = EikenApp()
    pyxel.run(app.update, app.draw)


if __name__ == "__main__":
    main()
