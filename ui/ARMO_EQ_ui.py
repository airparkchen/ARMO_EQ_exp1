# ui/ARMO_EQ_ui.py
import os
import json
import random
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from ui.PostQuestionnairePage import PostQuestionnairePage

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QPushButton, QRadioButton, QButtonGroup, QMessageBox, QLineEdit  
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from pathlib import Path

from ui.MusicPage import MusicPage

# =============================================================================
# 配置層
# =============================================================================

class MusicGenre(Enum):
    CLASSICAL = "古典"
    POP = "流行"  
    JAZZ = "爵士"

class MusicType(Enum):
    ORIGINAL = "原始"
    EQ_ENHANCED = "EQ調整"

@dataclass
class ExperimentConfig:
    """實驗配置"""
    total_rounds: int = 3
    music_base_path: str = "./music/"
    results_base_path: str = "./test_result/"
    questionnaire_path: str = "./ui/json/eq_experiment/"

@dataclass 
class MusicInfo:
    """音樂資訊"""
    genre: MusicGenre
    music_type: MusicType
    file_path: str
    round_number: int
    order_in_round: int

# =============================================================================
# 服務層
# =============================================================================

class MusicSequenceGenerator:
    """音樂序列生成器"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
    
    def generate_sequence(self) -> List[MusicInfo]:
        """生成隨機化音樂序列"""
        sequence = []
        genres = list(MusicGenre)
        random.shuffle(genres)  # 隨機音樂類型順序
        
        for round_num in range(1, self.config.total_rounds + 1):
            genre = genres[round_num - 1]
            music_types = list(MusicType)
            random.shuffle(music_types)  # 隨機EQ/原版順序
            
            for order, music_type in enumerate(music_types, 1):
                file_path = self._get_music_path(genre, music_type)
                sequence.append(MusicInfo(
                    genre=genre,
                    music_type=music_type,
                    file_path=file_path,
                    round_number=round_num,
                    order_in_round=order
                ))
        
        return sequence
        
    def _get_music_path(self, genre: MusicGenre, music_type: MusicType) -> str:
        """根據前綴 {genre}_{EQ|OM}* 尋找實際檔案（不綁 EQ 曲線名）"""
        genre_map = {
            MusicGenre.CLASSICAL: "classical",
            MusicGenre.POP: "pop",
            MusicGenre.JAZZ: "jazz"
        }
        folder = genre_map[genre]

        # 前綴：pop_EQ / pop_OM
        if music_type == MusicType.ORIGINAL:
            prefix = f"{folder}_OM"
        elif music_type == MusicType.EQ_ENHANCED:
            prefix = f"{folder}_EQ"
        else:
            raise ValueError(f"Unsupported music type: {music_type}")

        base_dir = Path(self.config.music_base_path).expanduser().resolve() / folder

        # 依副檔名的偏好順序尋找：先 wav，再 mp3，再 flac（可自行增減）
        ext_priority = [".wav", ".mp3", ".flac"]

        candidates = []
        for ext in ext_priority:
            # 兩種樣式都找：剛好等於前綴（pop_EQ.wav / pop_OM.wav）
            # 或是前綴加任意尾碼（pop_EQ_xxx.wav / pop_OM_xxx.wav）
            candidates += list(base_dir.glob(f"{prefix}{ext}"))
            candidates += list(base_dir.glob(f"{prefix}_*{ext}"))

        if not candidates:
            # 找不到就清楚說明預期位置與樣式
            raise FileNotFoundError(
                "找不到音檔。\n"
                f"搜尋資料夾：{base_dir}\n"
                f"前綴：{prefix}\n"
                f"嘗試副檔名：{', '.join(ext_priority)}\n"
                "請放入如 pop_EQ.wav、pop_EQ_任意名稱.wav、pop_OM.wav、pop_OM_任意名稱.wav 等檔案。"
            )

        # 若有多個候選：選「最後修改時間」最新的；同時也自然偏好前面較高優先的副檔名
        #（因為我們先按 ext_priority 蒐集，若修改時間相近，wav 通常會先進來）
        best = max(candidates, key=lambda p: p.stat().st_mtime)

        return str(best)
    
    def get_post_music_paths(self, genre: MusicGenre, round_music_sequence: List[MusicInfo]) -> tuple:
        """
        獲取後測問卷的音樂路徑
        
        Args:
            genre: 音樂類型
            round_music_sequence: 該輪的音樂序列（用來確定A/B段對應關係）
            
        Returns:
            tuple: (music_a_path, music_b_path)
        """
        genre_map = {
            MusicGenre.CLASSICAL: "classical",
            MusicGenre.POP: "pop",
            MusicGenre.JAZZ: "jazz"
        }
        folder = genre_map[genre]
        base_dir = Path(self.config.music_base_path).expanduser().resolve() / folder
        
        # 根據該輪的音樂序列確定A段和B段
        music_a_type = None  # 第一首音樂的類型
        music_b_type = None  # 第二首音樂的類型
        
        for music in round_music_sequence:
            if music.genre == genre:
                if music.order_in_round == 1:
                    music_a_type = music.music_type
                elif music.order_in_round == 2:
                    music_b_type = music.music_type
        
        # 查找後測音檔
        music_a_path = self._find_post_music_file(base_dir, folder, music_a_type)
        music_b_path = self._find_post_music_file(base_dir, folder, music_b_type)
        
        return music_a_path, music_b_path
    
    def _find_post_music_file(self, base_dir: Path, folder: str, music_type: MusicType) -> Optional[str]:
        """
        查找後測音樂檔案
        
        檔名格式：classical_EQ_post_*.* 或 classical_OM_post_*.*
        """
        if music_type is None:
            return None
        
        # 確定前綴
        if music_type == MusicType.ORIGINAL:
            prefix = f"{folder}_OM_post"
        elif music_type == MusicType.EQ_ENHANCED:
            prefix = f"{folder}_EQ_post"
        else:
            return None
        
        # 副檔名優先順序
        ext_priority = [".wav", ".mp3", ".flac"]
        
        candidates = []
        for ext in ext_priority:
            # 尋找符合格式的檔案：prefix.ext 或 prefix_*.ext
            candidates += list(base_dir.glob(f"{prefix}{ext}"))
            candidates += list(base_dir.glob(f"{prefix}_*{ext}"))
        
        if not candidates:
            print(f"[WARNING] 找不到後測音檔：{base_dir}/{prefix}*")
            return None
        
        # 選擇最新的檔案
        best = max(candidates, key=lambda p: p.stat().st_mtime)
        print(f"[DEBUG] 找到後測音檔：{best}")
        
        return str(best)

class DataManager:
    """數據管理器"""
    
    def __init__(self, case_path: str):
        self.case_path = case_path
        os.makedirs(case_path, exist_ok=True)
        
        # 新增：暫存每輪數據
        self.round_buffer = {}
    
    def save_questionnaire_results(self, results: List[Dict], qtype: str, 
                                 round_num: int = None, music_info: MusicInfo = None):
        """保存問卷結果 - 改為暫存模式"""
        
        # 如果沒有輪數，直接保存（保持原邏輯）
        if round_num is None:
            self._save_original_csv(results, qtype, music_info)
            return
        
        # 初始化輪次緩衝區
        if round_num not in self.round_buffer:
            self.round_buffer[round_num] = {
                'genre': None,
                'data': []
            }
        
        # 記錄音樂類型
        if music_info and self.round_buffer[round_num]['genre'] is None:
            self.round_buffer[round_num]['genre'] = music_info.genre.value
        
        # 為每筆數據添加相關信息
        for result in results:
            enhanced_result = result.copy()
            enhanced_result.update({
                'round': round_num,
                'phase': qtype,
                'music_type': music_info.music_type.value if music_info else '',
                'music_order': music_info.order_in_round if music_info else '',
                'music_file': os.path.basename(music_info.file_path) if music_info else ''
            })
            self.round_buffer[round_num]['data'].append(enhanced_result)
        
        # 如果是後測問卷，就整合保存該輪數據
        if qtype == "post_questionnaire":
            self._save_round_data(round_num)
    
    def _save_round_data(self, round_num: int):
        """保存整輪數據到單一檔案"""
        round_data = self.round_buffer[round_num]
        genre = round_data['genre'] or 'unknown'
        
        # 檔名格式：round_1_classical_complete.csv
        filename = f"round_{round_num}_{genre}_complete.csv"
        filepath = os.path.join(self.case_path, filename)
        
        # 寫入CSV
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'round', 'phase', 'question_id', 'question', 'answer', 
                'score', 'music_type', 'music_order', 'music_file', 'timestamp'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # 添加時間戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            for row in round_data['data']:
                row['timestamp'] = timestamp
                writer.writerow(row)
        
        print(f"✅ 第{round_num}輪數據已保存：{filename}")
        
        # 清除緩衝
        del self.round_buffer[round_num]
    
    def _save_original_csv(self, results: List[Dict], qtype: str, music_info: MusicInfo = None):
        """原始的CSV保存方法（保持不變）"""
        import csv
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{qtype}_{timestamp}.csv"
        filepath = os.path.join(self.case_path, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['question_id', 'question', 'answer', 'score', 'timestamp']
            if music_info:
                fieldnames.extend(['round', 'genre', 'music_type', 'order'])
                
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = result.copy()
                row['timestamp'] = timestamp
                if music_info:
                    row.update({
                        'round': music_info.round_number,
                        'genre': music_info.genre.value,
                        'music_type': music_info.music_type.value,
                        'order': music_info.order_in_round
                    })
                writer.writerow(row)
    
    def save_experiment_sequence(self, sequence: List[MusicInfo]):
        import csv
        
        filepath = os.path.join(self.case_path, "experiment_sequence.csv")
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['round', 'order', 'genre', 'music_type', 'file_path']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for music in sequence:
                writer.writerow({
                    'round': music.round_number,
                    'order': music.order_in_round,
                    'genre': music.genre.value,
                    'music_type': music.music_type.value,
                    'file_path': music.file_path
                })
class QuestionnaireLoader:
    """問卷載入器"""
    
    def __init__(self, questionnaire_path: str):
        self.path = questionnaire_path
    
    def load_questionnaire(self, filename: str) -> List[Dict]:
        """載入問卷JSON"""
        filepath = os.path.join(self.path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"載入問卷失敗: {e}")
            return []

# =============================================================================
# 介面層
# =============================================================================

class SimpleQuestionnairePage(QWidget):
    """簡單問卷頁面"""
    
    def __init__(self, questions: List[Dict], title: str, next_callback):
        super().__init__()
        self.questions = questions
        self.title = title
        self.next_callback = next_callback
        self.current_index = 0
        self.results = []
        
        self.init_ui()
        self.show_current_question()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)
        
        # 標題
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Arial", 22))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 問題
        self.question_label = QLabel()
        self.question_label.setFont(QFont("Arial", 20))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)
        
        # 選項區域
        self.options_layout = QVBoxLayout()
        layout.addLayout(self.options_layout)
        
        # 按鈕
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(50)
        
        self.prev_button = QPushButton("上一題")
        self.prev_button.setFont(QFont("Arial", 14))
        self.prev_button.setFixedSize(120, 50)
        self.prev_button.clicked.connect(self.prev_question)
        buttons_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("下一題")
        self.next_button.setFont(QFont("Arial", 14))
        self.next_button.setFixedSize(120, 50)
        self.next_button.clicked.connect(self.next_question)
        buttons_layout.addWidget(self.next_button)
        
        layout.addLayout(buttons_layout)
    
    def show_current_question(self):
        # 清空選項
        for i in reversed(range(self.options_layout.count())):
            child = self.options_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        question = self.questions[self.current_index]
        self.question_label.setText(question["question"])
        
        # 創建選項容器 - 整體居中，內容左對齊
        options_container = QWidget()
        options_container.setFixedWidth(500)  # 稍微窄一點適合一般問卷
        container_layout = QVBoxLayout(options_container)
        container_layout.setAlignment(Qt.AlignLeft)  # 選項內容左對齊
        container_layout.setSpacing(12)  # 選項間距
        container_layout.setContentsMargins(0, 10, 0, 10)

        is_multi_select = question.get("multi_select", False)
        
        if is_multi_select:
            #複選題
            self.checkboxes = []
            for option in question["options"]:
                checkbox = QCheckBox(option)
                checkbox.setFont(QFont("Arial", 14))
                checkbox.setStyleSheet("""
                    QCheckBox {
                        spacing: 10px;
                        padding: 8px;
                    }
                    QCheckBox::indicator {
                        width: 14px;
                        height: 14px;
                    }
                    QCheckBox::indicator:unchecked {
                        border: 2px solid #7f8c8d;
                        border-radius: 10px;
                        background-color: white;
                    }
                    QCheckBox::indicator:checked {
                        border: 2px solid #3498db;
                        border-radius: 10px;
                        background-color: #3498db;
                    }
                """)
                
                self.checkboxes.append(checkbox)
                container_layout.addWidget(checkbox)

        else:
            # 單選        
            # 創建選項
            self.button_group = QButtonGroup(self)
            for option in question["options"]:
                radio = QRadioButton(option)
                radio.setFont(QFont("Arial", 14))
                radio.setStyleSheet("""
                    QRadioButton {
                        spacing: 10px;
                        padding: 8px;
                    }
                    QRadioButton::indicator {
                        width: 14px;
                        height: 14px;
                    }
                    QRadioButton::indicator:unchecked {
                        border: 2px solid #7f8c8d;
                        border-radius: 10px;
                        background-color: white;
                    }
                    QRadioButton::indicator:checked {
                        border: 2px solid #3498db;
                        border-radius: 10px;
                        background-color: #3498db;
                    }
                """)
                
                self.button_group.addButton(radio)
                container_layout.addWidget(radio)
        
        # 將整個選項容器居中放置
        self.options_layout.setAlignment(Qt.AlignCenter)
        self.options_layout.addWidget(options_container)
        
        # 更新按鈕狀態
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setText("完成" if self.current_index == len(self.questions) - 1 else "下一題")

    
    def prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_question()
    
    def next_question(self):
        # 保存結果
        question = self.questions[self.current_index]
        is_multi_select = question.get("multi_select", False)

        if is_multi_select:
            #複選
            selected_options = []
            for checkbox in self.checkboxes:
                if checkbox.isChecked():
                    selected_options.append(checkbox.text())
            if not selected_options:
                QMessageBox.warning(selfm, "未選擇", "請至少選擇一個選項")
                return
            result = {
                "question_id": f"q{self.current_index + 1}",
                "question": question["question"],
                "answer": "; ".join(selected_options),
                "score": len(selected_options)
            }  
    
        else:
            #單選    
            # 檢查選擇
            selected = self.button_group.checkedButton()
            if not selected:
                QMessageBox.warning(self, "未選擇", "請選擇一個選項")
                return
            

            result = {
                "question_id": f"q{self.current_index + 1}",
                "question": question["question"],
                "answer": selected.text(),
                "score": question["options"].index(selected.text()) + 1
            }
        
        # 更新結果
        if self.current_index < len(self.results):
            self.results[self.current_index] = result
        else:
            self.results.append(result)
        
        # 下一題或完成
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.show_current_question()
        else:
            self.next_callback(self.results)

# =============================================================================
# 主視窗
# =============================================================================

class EQMusicExperimentWindow(QMainWindow):
    """EQ音樂實驗主視窗"""
    
    finished_signal = Signal(str)
    
    def __init__(self, debug_mode=False):  # 新增：除錯模式參數
        super().__init__()
        # 修改視窗標題顯示除錯狀態
        title = "EQ音樂效果實驗"
        if debug_mode:
            title += " [除錯模式]"
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.showMaximized()
        
        # 配置和狀態
        self.config = ExperimentConfig()
        self.debug_mode = debug_mode  # 新增：儲存除錯模式狀態
        self.current_round = 0
        self.current_phase = "start"
        self.first_round_completed = False
        
        # 服務初始化
        self.sequence_generator = MusicSequenceGenerator(self.config)
        self.questionnaire_loader = QuestionnaireLoader(self.config.questionnaire_path)
        # 參與者資訊
        self.participant_name = ""
        
        # 創建目錄和數據管理器
        self.case_path = self.create_case_directory()
        self.data_manager = DataManager(self.case_path)
        
        # 生成音樂序列
        self.music_sequence = self.sequence_generator.generate_sequence()
        self.data_manager.save_experiment_sequence(self.music_sequence)
        

        
        self.start_experiment()
        
    def create_case_directory(self) -> str:
        """創建實驗目錄 - 使用姓名+時間"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_name = f"{self.participant_name}_{timestamp}"
        case_path = os.path.join(self.config.results_base_path, case_name)
        os.makedirs(case_path, exist_ok=True)
        return case_path
    
    def start_experiment(self):
        """開始實驗頁面 - 添加簡單姓名輸入"""
        start_widget = QWidget()
        layout = QVBoxLayout(start_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("EQ音樂效果實驗")
        title.setFont(QFont("Arial", 32))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info = QLabel(
            f"本實驗將進行{self.config.total_rounds}輪音樂聆聽測試\n"
            "每輪包含：前測問卷 → 音樂1 → 評估 → 音樂2 → 評估 → 後測問卷\n\n"
            "請準備好耳機，確保環境安靜"
        )
        info.setFont(QFont("Arial", 18))
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # 姓名輸入 - 簡單版本
        name_label = QLabel("請輸入您的姓名：")
        name_label.setFont(QFont("Arial", 18))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 16))
        self.name_input.setFixedSize(200, 40)
        self.name_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)
        
        start_btn = QPushButton("開始實驗")
        start_btn.setFont(QFont("Arial", 20))
        start_btn.setFixedSize(150, 60)
        start_btn.clicked.connect(self.on_start_button_clicked)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)
        
        self.setCentralWidget(start_widget)

    def on_start_button_clicked(self):
        """開始按鈕點擊處理"""
        name = self.name_input.text().strip()
        
        if not name and not self.debug_mode:
            QMessageBox.warning(self, "提示", "請輸入姓名")
            return
        
        # 設定參與者姓名
        self.participant_name = name if name else "admin"
        
        # 創建實驗目錄
        self.case_path = self.create_case_directory()
        self.data_manager = DataManager(self.case_path)
        
        # 生成音樂序列
        self.music_sequence = self.sequence_generator.generate_sequence()
        self.data_manager.save_experiment_sequence(self.music_sequence)
        
        # 開始實驗
        self.start_first_round()
    
    def start_first_round(self):
        self.current_round = 1
        self.show_pre_questionnaire()
    
    def show_pre_questionnaire(self):
        questions = self.questionnaire_loader.load_questionnaire("pre_questionnaire.json")
        
        # 如果不是第一輪，過濾第一輪專用問題
        if self.first_round_completed:
            questions = [q for q in questions if not q.get("first_round_only", False)]
        
        questionnaire = SimpleQuestionnairePage(
            questions=questions,
            title=f"前測問卷 (第{self.current_round}輪)",
            next_callback=self.on_pre_questionnaire_complete
        )
        self.setCentralWidget(questionnaire)
    
    def on_pre_questionnaire_complete(self, results):
        self.data_manager.save_questionnaire_results(results, "pre_questionnaire", self.current_round)
        self.play_music(1)
        
    def play_music(self, music_number: int):
        """播放音樂 - 傳遞除錯模式參數"""
        music_info = self.get_current_music_info(music_number)
        if not music_info:
            QMessageBox.critical(self, "播放錯誤", f"找不到第 {music_number} 首的資訊。")
            return

        p = Path(music_info.file_path).expanduser().resolve()
        print(f"[DEBUG] 將播放音檔：{p}")
        if not p.exists() or p.stat().st_size == 0:
            QMessageBox.critical(
                self,
                "音檔不存在",
                f"找不到有效音檔：\n{p}\n\n請確認檔案已放到正確資料夾，且為有效的 WAV檔。"
            )
            return

        # 修改：傳遞除錯模式參數到 MusicPage
        music_page = MusicPage(
            music_path=str(p),
            next_page_callback=lambda: self.on_music_complete(music_number),
            debug_mode=self.debug_mode  # 新增：傳遞除錯模式
        )
        self.setCentralWidget(music_page)
    
    def get_current_music_info(self, music_number: int) -> Optional[MusicInfo]:
        for music in self.music_sequence:
            if (music.round_number == self.current_round and 
                music.order_in_round == music_number):
                return music
        return None
    
    def on_music_complete(self, music_number: int):
        self.show_music_evaluation(music_number)
    
    def show_music_evaluation(self, music_number: int):
        questions = self.questionnaire_loader.load_questionnaire("music_evaluation.json")
        music_info = self.get_current_music_info(music_number)
        
        questionnaire = SimpleQuestionnairePage(
            questions=questions,
            title=f"音樂{music_number}評估 (第{self.current_round}輪)",
            next_callback=lambda results: self.on_music_evaluation_complete(results, music_info)
        )
        self.setCentralWidget(questionnaire)
    
    def on_music_evaluation_complete(self, results, music_info):
        self.data_manager.save_questionnaire_results(
            results, "music_evaluation", self.current_round, music_info
        )
        
        if music_info.order_in_round == 1:
            self.play_music(2)  # 播放第二首
        else:
            self.show_post_questionnaire()  # 進入後測
    
    def show_post_questionnaire(self):
        """顯示後測問卷 - 支援音樂回放"""
        questions = self.questionnaire_loader.load_questionnaire("post_questionnaire.json")
        
        # 獲取該輪的音樂序列和類型
        current_round_music = [
            music for music in self.music_sequence 
            if music.round_number == self.current_round
        ]
        
        if current_round_music:
            # 獲取該輪的音樂類型
            genre = current_round_music[0].genre
            
            # 獲取後測音樂路徑
            music_a_path, music_b_path = self.sequence_generator.get_post_music_paths(
                genre, current_round_music
            )
            
            # 創建支援音樂回放的後測問卷頁面
            questionnaire = PostQuestionnairePage(
                questions=questions,
                title=f"後測問卷 (第{self.current_round}輪)",
                next_callback=self.on_post_questionnaire_complete,
                music_a_path=music_a_path,
                music_b_path=music_b_path,
                debug_mode=self.debug_mode
            )
        else:
            # 如果沒有找到音樂序列，使用原始簡單問卷頁面
            from ui.SimpleQuestionnairePage import SimpleQuestionnairePage  # 需要將原來的問卷頁面移到獨立檔案
            questionnaire = SimpleQuestionnairePage(
                questions=questions,
                title=f"後測問卷 (第{self.current_round}輪)",
                next_callback=self.on_post_questionnaire_complete
            )
        
        self.setCentralWidget(questionnaire)
    
    def on_post_questionnaire_complete(self, results):
        self.data_manager.save_questionnaire_results(results, "post_questionnaire", self.current_round)
        
        # 檢查是否還有下一輪
        if self.current_round < self.config.total_rounds:
            self.current_round += 1
            if self.current_round == 2:
                self.first_round_completed = True
            self.show_pre_questionnaire()
        else:
            self.complete_experiment()
    
    def complete_experiment(self):
        completion_widget = QWidget()
        layout = QVBoxLayout(completion_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("實驗完成！")
        title.setFont(QFont("Arial", 32))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info = QLabel("感謝您的參與！\n所有數據已保存完成。")
        info.setFont(QFont("Arial", 20))
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        close_btn = QPushButton("關閉")
        close_btn.setFont(QFont("Arial", 18))
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        self.setCentralWidget(completion_widget)
        self.finished_signal.emit(self.case_path)