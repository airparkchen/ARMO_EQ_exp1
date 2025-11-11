# ui/EventLogger.py
"""
實驗階段時間戳記錄器
用於記錄每個實驗階段的精確開始和結束時間
"""
import csv
import os
from datetime import datetime
from typing import Optional

class Phase:
    """實驗階段常數定義"""
    DEVICE_SETUP = "device_setup"
    BASELINE = "baseline"
    MUSIC1 = "music1"
    QUESTIONNAIRE1 = "questionnaire1"
    INTERVAL1 = "interval1"
    MUSIC2 = "music2"
    QUESTIONNAIRE2 = "questionnaire2"
    INTERVAL2 = "interval2"
    COMPLETE = "complete"

class EventLogger:
    """實驗事件時間戳記錄器"""

    def __init__(self, log_file_path: str):
        """
        初始化事件記錄器

        Args:
            log_file_path: 日誌檔案路徑 (CSV格式)
        """
        self.log_file_path = log_file_path
        self._initialize_log_file()

    def _initialize_log_file(self):
        """初始化日誌檔案，寫入表頭"""
        # 確保目錄存在
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

        # 創建檔案並寫入表頭
        with open(self.log_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'event_type', 'phase', 'music_id', 'notes'])

    def log_phase_start(self, phase: str, music_id: Optional[str] = None, notes: str = ""):
        """
        記錄階段開始

        Args:
            phase: 階段名稱 (使用 Phase 類別的常數)
            music_id: 音樂ID (如 "NA001")，可選
            notes: 備註，可選
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 精確到毫秒
        self._write_log(timestamp, "phase_start", phase, music_id or "", notes)
        print(f"[EventLog] {timestamp} - 開始階段: {phase}" + (f" ({music_id})" if music_id else ""))

    def log_phase_end(self, phase: str, music_id: Optional[str] = None, notes: str = ""):
        """
        記錄階段結束

        Args:
            phase: 階段名稱
            music_id: 音樂ID，可選
            notes: 備註，可選
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self._write_log(timestamp, "phase_end", phase, music_id or "", notes)
        print(f"[EventLog] {timestamp} - 結束階段: {phase}" + (f" ({music_id})" if music_id else ""))

    def log_custom_event(self, event_type: str, notes: str = ""):
        """
        記錄自定義事件

        Args:
            event_type: 事件類型
            notes: 備註
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self._write_log(timestamp, event_type, "", "", notes)
        print(f"[EventLog] {timestamp} - 自定義事件: {event_type}")

    def _write_log(self, timestamp: str, event_type: str, phase: str, music_id: str, notes: str):
        """寫入日誌到CSV檔案"""
        with open(self.log_file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event_type, phase, music_id, notes])
