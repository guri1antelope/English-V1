"""Storage management for Eiken Pre-2 App.

Handles multi-slot saves, browser LocalStorage synchronization,
input sanitization, and backup/restore (hikitsugi code).
"""

import base64
import datetime
import hashlib
import json
import os
import re

# Web環境（Pyodide / Pyxel Web）かどうかを検出
try:
    import js  # type: ignore

    IS_WEB = True
except ImportError:
    IS_WEB = False

MAX_SLOTS = 4


def get_local_today_str() -> str:
    """端末の現地日付 (YYYY-MM-DD) を取得。Web環境ではブラウザのローカル時間を優先。"""
    if IS_WEB:
        try:
            val = str(js.eval("new Date().toLocaleDateString('sv')"))
            if len(val) == 10 and val[4] == "-" and val[7] == "-":
                return val
        except Exception:
            pass
    return datetime.date.today().isoformat()


def sanitize_player_name(name: str) -> str:
    """プレイヤー名を安全な文字列にサニタイズ（最大8文字、記号排除）。"""
    # ひらがな、カタカナ、漢字、英数字のみ許可
    cleaned = re.sub(r"[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]", "", name)
    return cleaned[:8] if cleaned else "たろう"


def get_default_slot_data(slot_id: int, player_name: str, partner_id: int) -> dict:
    """初期セーブデータを生成。"""
    today_str = get_local_today_str()
    return {
        "slot_id": slot_id,
        "player_name": sanitize_player_name(player_name),
        "partner": {
            "id": partner_id,  # 1:柴犬, 2:子猫, 3:ウサギ, 4:リス, 5:ペンギン
            "stage": 1,  # 1:タマゴ, 2:幼体, 3:成体, 4:究極体
            "level": 1,
            "exp": 0,
            "fullness": 80,  # 0〜100
        },
        "food_inventory": {
            "apple": 3,
            "meat": 1,
            "golden_apple": 1,
        },
        "streak": 1,
        "last_date": today_str,
        "last_login_date": "",
        "last_daily_challenge_date": "",
        "cleared_lessons": {},  # "L01": {"cleared": True, "stars": 3}
        "duo_cleared_sections": {},  # "1": {"cleared": True, "stars": 3}
        "mastery": {},  # "L01_Q001": {"score": 80, "interval": 1, "next_review": "2026-10-23"}
    }


class StorageManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.slots = {}
        self.load_all_slots()

    def _get_file_path(self, slot_id: int) -> str:
        return os.path.join(self.data_dir, f"save_slot_{slot_id}.json")

    def _get_storage_key(self, slot_id: int) -> str:
        return f"eiken_pre2_slot_{slot_id}"

    def load_slot(self, slot_id: int) -> dict | None:
        """スロットからセーブデータを読み込む。"""
        slot_data = None
        # 1. WebブラウザのLocalStorageからの読み込み
        if IS_WEB:
            try:
                raw_data = js.window.localStorage.getItem(self._get_storage_key(slot_id))
                if raw_data:
                    slot_data = json.loads(str(raw_data))
            except Exception:
                pass

        # 2. ローカルファイルからの読み込み（Web環境ではLocalStorageのみを参照し、同梱ファイルは読まない）
        if not slot_data and not IS_WEB:
            path = self._get_file_path(slot_id)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        slot_data = json.load(f)
                except Exception:
                    pass

        if slot_data and isinstance(slot_data, dict):
            # 破損・旧形式データの自己修復
            slot_data.setdefault("slot_id", slot_id)
            slot_data.setdefault("player_name", "たろう")
            
            # partner の堅牢化
            partner = slot_data.get("partner")
            if not isinstance(partner, dict):
                partner = {"id": 1, "stage": 1, "level": 1, "exp": 0, "fullness": 80}
                slot_data["partner"] = partner
            else:
                partner.setdefault("id", 1)
                partner.setdefault("stage", 1)
                partner.setdefault("level", 1)
                partner.setdefault("exp", 0)
                partner.setdefault("fullness", 80)
                # partner_id の範囲チェック (1〜5)
                try:
                    pid = int(partner.get("id", 1))
                    if pid < 1 or pid > 5:
                        partner["id"] = 1
                except Exception:
                    partner["id"] = 1
                try:
                    stg = int(partner.get("stage", 1))
                    if stg < 1 or stg > 4:
                        partner["stage"] = 1
                except Exception:
                    partner["stage"] = 1

            # cleared_lessons / duo_cleared_sections
            if not isinstance(slot_data.get("cleared_lessons"), dict):
                slot_data["cleared_lessons"] = {}
            if not isinstance(slot_data.get("duo_cleared_sections"), dict):
                slot_data["duo_cleared_sections"] = {}
            if not isinstance(slot_data.get("mastery"), dict):
                slot_data["mastery"] = {}

            slot_data.setdefault("streak", 1)
            slot_data.setdefault("last_date", "")
            slot_data.setdefault("last_login_date", "")
            slot_data.setdefault("last_daily_challenge_date", "")

            # food_inventory
            food = slot_data.get("food_inventory")
            if not isinstance(food, dict):
                food = {"apple": 3, "meat": 1, "golden_apple": 1}
                slot_data["food_inventory"] = food
            else:
                food.setdefault("apple", 3)
                food.setdefault("meat", 1)
                food.setdefault("golden_apple", 1)

            return slot_data

        return None

    def load_all_slots(self):
        """全スロットをメモリにロード。"""
        for s in range(1, MAX_SLOTS + 1):
            self.slots[s] = self.load_slot(s)

    def save_slot(self, slot_id: int, data: dict) -> bool:
        """セーブデータを保存（ブラウザLocalStorageおよびファイル）。"""
        if slot_id < 1 or slot_id > MAX_SLOTS:
            return False

        data["slot_id"] = slot_id
        # 日付・ストリーク更新チェック
        today = get_local_today_str()
        last_date = data.get("last_date")
        if last_date and last_date != today:
            # 連続日数の判定
            try:
                d_last = datetime.date.fromisoformat(last_date)
                d_today = datetime.date.fromisoformat(today)
                diff = (d_today - d_last).days
                if diff == 1:
                    data["streak"] = data.get("streak", 1) + 1
                elif diff > 1:
                    data["streak"] = 1
            except Exception:
                pass
        data["last_date"] = today

        self.slots[slot_id] = data
        json_str = json.dumps(data, ensure_ascii=False, indent=2)

        # 1. WebブラウザのLocalStorageに保存
        if IS_WEB:
            try:
                js.window.localStorage.setItem(self._get_storage_key(slot_id), json_str)
            except Exception:
                pass

        # 2. ローカルファイルに保存
        try:
            with open(self._get_file_path(slot_id), "w", encoding="utf-8") as f:
                f.write(json_str)
            return True
        except Exception:
            return False

    def delete_slot(self, slot_id: int) -> bool:
        """スロットデータを削除。"""
        self.slots[slot_id] = None
        if IS_WEB:
            try:
                js.window.localStorage.removeItem(self._get_storage_key(slot_id))
            except Exception:
                pass
        path = self._get_file_path(slot_id)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                return False
        return True

    # -------------------------------------------------------------
    # バックアップ / 引き継ぎコード機能
    # -------------------------------------------------------------
    def export_backup_code(self, slot_id: int) -> str:
        """スロットデータを引き継ぎコード（Base64＋チェックサム）として出力。"""
        data = self.slots.get(slot_id)
        if not data:
            return ""

        json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        # 簡易チェックサム（SHA-256先頭6文字）
        checksum = hashlib.sha256(json_bytes).hexdigest()[:6]
        b64 = base64.b64encode(json_bytes).decode("ascii")
        return f"EK2-{checksum}-{b64}"

    def import_backup_code(self, slot_id: int, code: str) -> bool:
        """引き継ぎコードを検証してスロットに復元。"""
        try:
            clean_code = code.strip()
            if not clean_code.startswith("EK2-"):
                return False

            parts = clean_code.split("-", 2)
            if len(parts) != 3:
                return False

            expected_checksum = parts[1]
            b64_payload = parts[2]

            json_bytes = base64.b64decode(b64_payload.encode("ascii"))
            actual_checksum = hashlib.sha256(json_bytes).hexdigest()[:6]

            if expected_checksum != actual_checksum:
                return False  # 改ざんまたは破損

            data = json.loads(json_bytes.decode("utf-8"))
            return self.save_slot(slot_id, data)
        except Exception:
            return False
