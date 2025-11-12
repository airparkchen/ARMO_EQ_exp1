# ui/NewExperimentWindowWithBio.py
"""
新實驗主控制器 - 整合生理訊號記錄
流程：設備配戴 → Baseline(3分鐘) → 音樂1(5分鐘) → 問卷1 → 間隔1(至少3分鐘)
     → 音樂2(5分鐘) → 問卷2 → 間隔2(至少3分鐘) → 完成

整合功能：
- 在實驗開始時自動啟動生理訊號記錄
- 在每個階段切換時自動標記 label
- 實驗結束時自動停止記錄
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QMessageBox, QRadioButton, QButtonGroup, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.BaselinePage import BaselinePage
from ui.MusicPageWithTimer import MusicPageWithTimer
from ui.IntervalPage import IntervalPage
from ui.ARMO_EQ_ui import SimpleQuestionnairePage
from ui.EventLogger import EventLogger, Phase

# 導入生理訊號模組
from bio_signal.bio_signal_manager import BioSignalManager
from labels.LabelManager import LabelManager

# =============================================================================
# 配置類別
# =============================================================================

class ExperimentConfig:
    """新實驗配置"""
    # 時間設定（秒）
    BASELINE_DURATION = 180      # 3分鐘
    MUSIC_DURATION = 300         # 5分鐘
    INTERVAL_MIN_DURATION = 180  # 至少3分鐘

    # 受測者設定
    TOTAL_SUBJECTS = 30
    TOTAL_SESSIONS = 6

    # 路徑設定
    music_base_path = "./music/"
    results_base_path = "./test_result/"
    catalog_path = "./music_catalog.json"
    questionnaire_path = "./ui/json/new_experiment/"
    labels_path = "./labels/experiment_labels.json"

    # 生理訊號設定
    bio_signal_host = "0.0.0.0"
    bio_signal_port = 8000

# =============================================================================
# 主視窗
# =============================================================================

class NewExperimentWindowWithBio(QMainWindow):
    """新實驗主視窗 - 整合生理訊號"""

    def __init__(self, debug_mode: bool = False):
        super().__init__()
        self.debug_mode = debug_mode

        # 視窗設定
        title = "音樂實驗系統 - 生理訊號版"
        if debug_mode:
            title += " [除錯模式]"
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.showMaximized()

        # 實驗參數
        self.subject_id = None
        self.session_number = None
        self.group = None
        self.category = None
        self.category_code = None
        self.enable_bio_signal = False  # 是否啟用生理訊號記錄

        # 音樂資訊
        self.music_catalog = None
        self.song_order = []
        self.music_files = []

        # 配置和服務
        self.config = ExperimentConfig()
        self.event_logger = None
        self.result_dir = None

        # 生理訊號管理器
        self.label_manager = None
        self.bio_signal_manager = None
        self.current_page_index = 0  # 追蹤當前頁面索引

        # 載入音樂目錄
        self.load_music_catalog()

        # 載入標籤管理器
        self.load_label_manager()

        # 顯示開始頁面
        self.show_start_page()

    def load_music_catalog(self):
        """載入音樂目錄JSON"""
        try:
            with open(self.config.catalog_path, 'r', encoding='utf-8') as f:
                self.music_catalog = json.load(f)
            print(f"[系統] 成功載入音樂目錄：{len(self.music_catalog['categories'])} 個類別")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入音樂目錄失敗：{str(e)}")
            self.music_catalog = {"categories": []}

    def load_label_manager(self):
        """載入標籤管理器"""
        try:
            self.label_manager = LabelManager(self.config.labels_path)
            print(f"[系統] 成功載入標籤管理器")
        except Exception as e:
            print(f"[警告] 載入標籤管理器失敗：{e}")
            self.label_manager = None

    def show_start_page(self):
        """開始頁面 - 輸入實驗參數"""
        start_widget = QWidget()
        layout = QVBoxLayout(start_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(60, 40, 60, 40)

        # 標題
        title = QLabel("音樂實驗系統")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 說明
        info = QLabel(
            "請設定實驗參數\n"
            "每次實驗將播放2首音樂，總時長約15-20分鐘"
        )
        info.setFont(QFont("Arial", 16))
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addSpacing(20)

        # 參數輸入區域
        params_layout = QVBoxLayout()
        params_layout.setSpacing(15)

        # 受測者ID
        subject_layout = QHBoxLayout()
        subject_label = QLabel("受測者編號 (1-30):")
        subject_label.setFont(QFont("Arial", 16))
        subject_label.setFixedWidth(200)
        self.subject_combo = QComboBox()
        self.subject_combo.addItems([str(i) for i in range(1, 31)])
        self.subject_combo.setFont(QFont("Arial", 14))
        self.subject_combo.setFixedWidth(100)
        subject_layout.addWidget(subject_label)
        subject_layout.addWidget(self.subject_combo)
        subject_layout.addStretch()
        params_layout.addLayout(subject_layout)

        # Session編號
        session_layout = QHBoxLayout()
        session_label = QLabel("第幾次來 (1-6):")
        session_label.setFont(QFont("Arial", 16))
        session_label.setFixedWidth(200)
        self.session_combo = QComboBox()
        self.session_combo.addItems([str(i) for i in range(1, 7)])
        self.session_combo.setFont(QFont("Arial", 14))
        self.session_combo.setFixedWidth(100)
        session_layout.addWidget(session_label)
        session_layout.addWidget(self.session_combo)
        session_layout.addStretch()
        params_layout.addLayout(session_layout)

        # 音樂類別
        category_layout = QHBoxLayout()
        category_label = QLabel("音樂類別:")
        category_label.setFont(QFont("Arial", 16))
        category_label.setFixedWidth(200)
        self.category_combo = QComboBox()
        category_names = [cat['display_name'] for cat in self.music_catalog['categories']]
        self.category_combo.addItems(category_names)
        self.category_combo.setFont(QFont("Arial", 14))
        self.category_combo.setFixedWidth(300)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        params_layout.addLayout(category_layout)

        # 組別選擇
        group_layout = QHBoxLayout()
        group_label = QLabel("組別:")
        group_label.setFont(QFont("Arial", 16))
        group_label.setFixedWidth(200)

        self.group_button_group = QButtonGroup()
        self.group_a_radio = QRadioButton("A組 (001→002)")
        self.group_b_radio = QRadioButton("B組 (002→001)")
        self.group_a_radio.setFont(QFont("Arial", 14))
        self.group_b_radio.setFont(QFont("Arial", 14))
        self.group_a_radio.setChecked(True)

        self.group_button_group.addButton(self.group_a_radio)
        self.group_button_group.addButton(self.group_b_radio)

        group_layout.addWidget(group_label)
        group_layout.addWidget(self.group_a_radio)
        group_layout.addWidget(self.group_b_radio)
        group_layout.addStretch()
        params_layout.addLayout(group_layout)

        # ⭐ 新增：生理訊號記錄選項
        bio_layout = QHBoxLayout()
        bio_label = QLabel("生理訊號記錄:")
        bio_label.setFont(QFont("Arial", 16))
        bio_label.setFixedWidth(200)

        self.bio_checkbox = QCheckBox("啟用生理訊號記錄")
        self.bio_checkbox.setFont(QFont("Arial", 14))
        self.bio_checkbox.setChecked(False)  # 預設關閉

        bio_layout.addWidget(bio_label)
        bio_layout.addWidget(self.bio_checkbox)
        bio_layout.addStretch()
        params_layout.addLayout(bio_layout)

        layout.addLayout(params_layout)
        layout.addSpacing(30)

        # 開始按鈕
        start_btn = QPushButton("開始實驗")
        start_btn.setFont(QFont("Arial", 20, QFont.Bold))
        start_btn.setFixedSize(200, 70)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        start_btn.clicked.connect(self.on_start_experiment)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        self.setCentralWidget(start_widget)

    def on_start_experiment(self):
        """開始實驗按鈕點擊"""
        # 取得參數
        self.subject_id = int(self.subject_combo.currentText())
        self.session_number = int(self.session_combo.currentText())
        self.group = 'A' if self.group_a_radio.isChecked() else 'B'
        self.enable_bio_signal = self.bio_checkbox.isChecked()

        # 取得選擇的類別
        selected_index = self.category_combo.currentIndex()
        selected_category = self.music_catalog['categories'][selected_index]
        self.category = selected_category['name']
        self.category_code = selected_category['code']

        # 決定播放順序
        if self.group == 'A':
            self.song_order = ['001', '002']
        else:
            self.song_order = ['002', '001']

        # 檢查音檔是否存在
        if not self.check_music_files():
            return

        # 創建結果目錄
        self.create_result_directory()

        # 初始化EventLogger
        log_path = os.path.join(self.result_dir, "event_log.csv")
        self.event_logger = EventLogger(log_path)

        # 保存實驗資訊
        self.save_experiment_info()

        # ⭐ 初始化生理訊號管理器
        if self.enable_bio_signal:
            self.initialize_bio_signal()

        # 開始實驗流程
        self.start_baseline()

    def initialize_bio_signal(self):
        """初始化生理訊號記錄"""
        try:
            self.bio_signal_manager = BioSignalManager(self.label_manager)

            # 開始讀取生理訊號（建立連線）
            self.bio_signal_manager.start_reading(
                case_path=self.result_dir,
                host=self.config.bio_signal_host,
                port=self.config.bio_signal_port
            )

            print(f"[生理訊號] 已初始化，等待連線於 {self.config.bio_signal_host}:{self.config.bio_signal_port}")

        except Exception as e:
            QMessageBox.warning(
                self,
                "生理訊號初始化失敗",
                f"無法初始化生理訊號記錄：{str(e)}\n\n實驗將繼續，但不會記錄生理訊號。"
            )
            self.enable_bio_signal = False
            self.bio_signal_manager = None

    def update_bio_signal_label(self, page_index: int, phase_name: str):
        """更新生理訊號標籤"""
        if not self.enable_bio_signal or not self.bio_signal_manager:
            return

        try:
            # 從 LabelManager 獲取標籤配置
            label_config = self.label_manager.get_label_for_page(page_index)

            if label_config:
                label = label_config['label']
                # 設定標籤到生理訊號系統
                self.bio_signal_manager.set_current(label)
                # 標記事件
                self.bio_signal_manager.mark_label_event(label)
                print(f"[生理訊號] 標籤更新：{label} (頁面{page_index})")
            else:
                print(f"[警告] 找不到頁面 {page_index} 的標籤配置")

        except Exception as e:
            print(f"[錯誤] 更新生理訊號標籤失敗：{e}")

    def check_music_files(self) -> bool:
        """檢查音樂檔案是否存在"""
        self.music_files = []

        for song_id in self.song_order:
            filename = f"{self.category_code}{song_id}.wav"
            file_path = Path(self.config.music_base_path) / self.category / filename

            if not file_path.exists():
                QMessageBox.critical(
                    self,
                    "音檔不存在",
                    f"找不到音檔：\n{file_path}\n\n請確認檔案已放置正確。"
                )
                return False

            self.music_files.append(str(file_path))

        print(f"[系統] 音檔檢查通過：{self.music_files}")
        return True

    def create_result_directory(self):
        """創建結果目錄"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bio_suffix = "_BIO" if self.enable_bio_signal else ""
        dir_name = f"P{self.subject_id:03d}_S{self.session_number}_G{self.group}{bio_suffix}_{timestamp}"
        self.result_dir = os.path.join(self.config.results_base_path, dir_name)
        os.makedirs(self.result_dir, exist_ok=True)
        print(f"[系統] 創建結果目錄：{self.result_dir}")

    def save_experiment_info(self):
        """保存實驗參數資訊"""
        info = {
            "subject_id": self.subject_id,
            "session_number": self.session_number,
            "group": self.group,
            "category": self.category,
            "category_code": self.category_code,
            "song_order": self.song_order,
            "music_files": [os.path.basename(f) for f in self.music_files],
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "debug_mode": self.debug_mode,
            "bio_signal_enabled": self.enable_bio_signal,
            "bio_signal_host": self.config.bio_signal_host if self.enable_bio_signal else None,
            "bio_signal_port": self.config.bio_signal_port if self.enable_bio_signal else None
        }

        info_path = os.path.join(self.result_dir, "experiment_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        print(f"[系統] 保存實驗資訊：{info_path}")

    # =========================================================================
    # 實驗流程控制（整合生理訊號標記）
    # =========================================================================

    def start_baseline(self):
        """開始Baseline階段"""
        self.current_page_index = 1  # baseline
        self.event_logger.log_phase_start(Phase.BASELINE)
        self.update_bio_signal_label(self.current_page_index, "baseline")

        baseline_page = BaselinePage(
            duration_seconds=self.config.BASELINE_DURATION,
            next_callback=self.on_baseline_complete,
            debug_mode=self.debug_mode
        )
        self.setCentralWidget(baseline_page)

    def on_baseline_complete(self):
        """Baseline完成"""
        self.event_logger.log_phase_end(Phase.BASELINE)
        self.play_music_1()

    def play_music_1(self):
        """播放音樂1"""
        self.current_page_index = 2  # music1
        music_id = f"{self.category_code}{self.song_order[0]}"
        self.event_logger.log_phase_start(Phase.MUSIC1, music_id)
        self.update_bio_signal_label(self.current_page_index, "music1")

        music_page = MusicPageWithTimer(
            music_path=self.music_files[0],
            music_title=f"{self.category} - {music_id}",
            duration_seconds=self.config.MUSIC_DURATION,
            next_page_callback=self.on_music1_complete,
            debug_mode=self.debug_mode
        )
        self.setCentralWidget(music_page)

    def on_music1_complete(self):
        """音樂1完成"""
        music_id = f"{self.category_code}{self.song_order[0]}"
        self.event_logger.log_phase_end(Phase.MUSIC1, music_id)
        self.show_questionnaire_1()

    def show_questionnaire_1(self):
        """顯示問卷1"""
        self.current_page_index = 3  # questionnaire1
        self.event_logger.log_phase_start(Phase.QUESTIONNAIRE1)
        self.update_bio_signal_label(self.current_page_index, "questionnaire1")

        questions = self.load_questionnaire()
        questionnaire = SimpleQuestionnairePage(
            questions=questions,
            title="音樂1 評估問卷",
            next_callback=self.on_questionnaire1_complete
        )
        self.setCentralWidget(questionnaire)

    def on_questionnaire1_complete(self, results: List[Dict]):
        """問卷1完成"""
        self.event_logger.log_phase_end(Phase.QUESTIONNAIRE1)
        self.save_questionnaire_results(results, "music1_evaluation")
        self.start_interval_1()

    def start_interval_1(self):
        """開始間隔1"""
        self.current_page_index = 4  # interval1
        self.event_logger.log_phase_start(Phase.INTERVAL1)
        self.update_bio_signal_label(self.current_page_index, "interval1")

        interval_page = IntervalPage(
            min_duration_seconds=self.config.INTERVAL_MIN_DURATION,
            next_callback=self.on_interval1_complete,
            debug_mode=self.debug_mode
        )
        self.setCentralWidget(interval_page)

    def on_interval1_complete(self):
        """間隔1完成"""
        self.event_logger.log_phase_end(Phase.INTERVAL1)
        self.play_music_2()

    def play_music_2(self):
        """播放音樂2"""
        self.current_page_index = 5  # music2
        music_id = f"{self.category_code}{self.song_order[1]}"
        self.event_logger.log_phase_start(Phase.MUSIC2, music_id)
        self.update_bio_signal_label(self.current_page_index, "music2")

        music_page = MusicPageWithTimer(
            music_path=self.music_files[1],
            music_title=f"{self.category} - {music_id}",
            duration_seconds=self.config.MUSIC_DURATION,
            next_page_callback=self.on_music2_complete,
            debug_mode=self.debug_mode
        )
        self.setCentralWidget(music_page)

    def on_music2_complete(self):
        """音樂2完成"""
        music_id = f"{self.category_code}{self.song_order[1]}"
        self.event_logger.log_phase_end(Phase.MUSIC2, music_id)
        self.show_questionnaire_2()

    def show_questionnaire_2(self):
        """顯示問卷2"""
        self.current_page_index = 6  # questionnaire2
        self.event_logger.log_phase_start(Phase.QUESTIONNAIRE2)
        self.update_bio_signal_label(self.current_page_index, "questionnaire2")

        questions = self.load_questionnaire()
        questionnaire = SimpleQuestionnairePage(
            questions=questions,
            title="音樂2 評估問卷",
            next_callback=self.on_questionnaire2_complete
        )
        self.setCentralWidget(questionnaire)

    def on_questionnaire2_complete(self, results: List[Dict]):
        """問卷2完成"""
        self.event_logger.log_phase_end(Phase.QUESTIONNAIRE2)
        self.save_questionnaire_results(results, "music2_evaluation")
        self.start_interval_2()

    def start_interval_2(self):
        """開始間隔2"""
        self.current_page_index = 7  # interval2
        self.event_logger.log_phase_start(Phase.INTERVAL2)
        self.update_bio_signal_label(self.current_page_index, "interval2")

        interval_page = IntervalPage(
            min_duration_seconds=self.config.INTERVAL_MIN_DURATION,
            next_callback=self.on_interval2_complete,
            debug_mode=self.debug_mode
        )
        self.setCentralWidget(interval_page)

    def on_interval2_complete(self):
        """間隔2完成"""
        self.event_logger.log_phase_end(Phase.INTERVAL2)
        self.complete_experiment()

    def complete_experiment(self):
        """完成實驗"""
        self.current_page_index = 8  # complete
        self.event_logger.log_phase_start(Phase.COMPLETE)
        self.update_bio_signal_label(self.current_page_index, "complete")

        # ⭐ 關閉生理訊號記錄
        if self.enable_bio_signal and self.bio_signal_manager:
            try:
                self.bio_signal_manager.close()
                print("[生理訊號] 已關閉記錄")
            except Exception as e:
                print(f"[錯誤] 關閉生理訊號記錄失敗：{e}")

        completion_widget = QWidget()
        layout = QVBoxLayout(completion_widget)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("✓ 實驗完成！")
        title.setFont(QFont("Arial", 40, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #27ae60;")
        layout.addWidget(title)

        info_text = (
            "感謝您的參與！\n\n"
            f"受測者編號：P{self.subject_id:03d}\n"
            f"Session：{self.session_number}/6\n"
            f"音樂類別：{self.category}\n"
            f"生理訊號記錄：{'已啟用' if self.enable_bio_signal else '未啟用'}\n\n"
            "所有數據已保存完成。"
        )

        info = QLabel(info_text)
        info.setFont(QFont("Arial", 20))
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        close_btn = QPushButton("關閉")
        close_btn.setFont(QFont("Arial", 18))
        close_btn.setFixedSize(150, 60)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.setCentralWidget(completion_widget)

    # =========================================================================
    # 輔助方法
    # =========================================================================

    def load_questionnaire(self) -> List[Dict]:
        """載入問卷"""
        try:
            questionnaire_file = os.path.join(
                self.config.questionnaire_path,
                "music_evaluation_new.json"
            )
            with open(questionnaire_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[錯誤] 載入問卷失敗：{e}")
            return []

    def save_questionnaire_results(self, results: List[Dict], filename_prefix: str):
        """保存問卷結果"""
        import csv

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(self.result_dir, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['question_id', 'question', 'dimension', 'answer', 'score', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                questions = self.load_questionnaire()
                q_index = int(result['question_id'][1:]) - 1
                dimension = questions[q_index].get('dimension', '') if q_index < len(questions) else ''

                row = {
                    'question_id': result['question_id'],
                    'question': result['question'],
                    'dimension': dimension,
                    'answer': result['answer'],
                    'score': result['score'],
                    'timestamp': timestamp
                }
                writer.writerow(row)

        print(f"[系統] 保存問卷結果：{filename}")

    def closeEvent(self, event):
        """視窗關閉事件"""
        # 確保關閉生理訊號記錄
        if self.enable_bio_signal and self.bio_signal_manager:
            try:
                self.bio_signal_manager.close()
                print("[生理訊號] 視窗關閉，已停止記錄")
            except Exception as e:
                print(f"[錯誤] 關閉生理訊號記錄失敗：{e}")

        super().closeEvent(event)
