# ui/PostQuestionnairePage.py - 新檔案
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QRadioButton, QButtonGroup, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl
from pathlib import Path
from typing import List, Dict, Optional

class PostQuestionnairePage(QWidget):
    """後測問卷頁面 - 支援音樂回放"""
    
    def __init__(self, questions: List[Dict], title: str, next_callback, 
                 music_a_path: str = None, music_b_path: str = None, debug_mode: bool = False):
        super().__init__()
        self.questions = questions
        self.title = title
        self.next_callback = next_callback
        self.music_a_path = music_a_path
        self.music_b_path = music_b_path
        self.debug_mode = debug_mode
        
        self.current_index = 0
        self.results = []
        
        # 音樂播放器
        self.player = None
        self.audio_output = None
        self.init_audio()
        
        self.init_ui()
        self.show_current_question()
    
    def init_audio(self):
        """初始化音訊播放器"""
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)
        self.player.setAudioOutput(self.audio_output)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)
        
        # 標題
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Arial", 28))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 音樂回放控制區域
        if self.music_a_path or self.music_b_path:
            self.create_music_control_section(layout)
        
        # 問題區域
        self.question_label = QLabel()
        self.question_label.setFont(QFont("Arial", 24))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)
        
        # 選項區域
        self.options_layout = QVBoxLayout()
        layout.addLayout(self.options_layout)
        
        # 按鈕區域
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(50)
        
        self.prev_button = QPushButton("上一題")
        self.prev_button.setFont(QFont("Arial", 20))
        self.prev_button.setFixedSize(120, 50)
        self.prev_button.clicked.connect(self.prev_question)
        buttons_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("下一題")
        self.next_button.setFont(QFont("Arial", 20))
        self.next_button.setFixedSize(120, 50)
        self.next_button.clicked.connect(self.next_question)
        buttons_layout.addWidget(self.next_button)
        
        layout.addLayout(buttons_layout)
    
    def create_music_control_section(self, layout: QVBoxLayout):
        """創建音樂回放控制區域"""
        music_frame = QFrame()
        music_frame.setFrameStyle(QFrame.Box)
        music_frame.setStyleSheet("""
            QFrame { 
                background-color: #fafafa; 
                border: 2px solid #2c3e50; 
                border-radius: 12px;
                margin: 10px;
                padding: 10px;
            }
        """)
        music_layout = QVBoxLayout(music_frame)
        
        # 標題
        music_title = QLabel("🎵 需重新聆聽音樂片段來協助回答，請點擊下方按鈕：")
        music_title.setFont(QFont("Arial", 20, QFont.Bold))
        music_title.setAlignment(Qt.AlignCenter)
        music_title.setStyleSheet("color: #2c3e50; margin: 8px;")
        music_layout.addWidget(music_title)
        
        # # 說明文字
        # instruction = QLabel("如需重新聆聽音樂片段來協助回答，請點擊下方按鈕：")
        # instruction.setFont(QFont("Arial", 16))
        # instruction.setAlignment(Qt.AlignCenter)
        # instruction.setWordWrap(True)
        # instruction.setStyleSheet("color: #34495e; margin: 5px;")
        # music_layout.addWidget(instruction)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(40)
        
        # A段音樂按鈕
        if self.music_a_path:
            self.play_a_button = QPushButton("🎵 播放 A 段音樂")
            self.play_a_button.setFont(QFont("Arial", 16, QFont.Bold))
            self.play_a_button.setFixedSize(200, 60)
            self.play_a_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            self.play_a_button.clicked.connect(self.play_music_a)
            button_layout.addWidget(self.play_a_button)
        
        # 停止按鈕 (移到中間位置)
        self.stop_button = QPushButton("⏹ 停止播放")
        self.stop_button.setFont(QFont("Arial", 14))
        self.stop_button.setFixedSize(140, 45)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #6c7b7d;
            }
            QPushButton:pressed {
                background-color: #5d6d6e;
            }
        """)
        self.stop_button.clicked.connect(self.stop_music)
        button_layout.addWidget(self.stop_button)
        
        # B段音樂按鈕
        if self.music_b_path:
            self.play_b_button = QPushButton("🎵 播放 B 段音樂")
            self.play_b_button.setFont(QFont("Arial", 16, QFont.Bold))
            self.play_b_button.setFixedSize(200, 60)
            self.play_b_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            self.play_b_button.clicked.connect(self.play_music_b)
            button_layout.addWidget(self.play_b_button)
        
        music_layout.addLayout(button_layout)
        
        # 第二排按鈕區域
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignCenter)
        control_layout.setSpacing(30)
        
        # 除錯模式跳過按鈕
        # if self.debug_mode:
        #     skip_button = QPushButton("⏭ 跳過音樂")
        #     skip_button.setFont(QFont("Arial", 14))
        #     skip_button.setFixedSize(130, 40)
        #     skip_button.setStyleSheet("""
        #         QPushButton {
        #             background-color: #ff6666;
        #             color: white;
        #             border: none;
        #             border-radius: 5px;
        #         }
        #         QPushButton:hover {
        #             background-color: #ff4444;
        #         }
        #     """)
        #     skip_button.clicked.connect(self.stop_music)
        #     control_layout.addWidget(skip_button)
        
        music_layout.addLayout(control_layout)
        
        # 播放狀態顯示
        self.status_label = QLabel("♪ 狀態：待機中")
        self.status_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #2c3e50; 
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 6px;
            padding: 6px;
            margin: 8px;
        """)
        music_layout.addWidget(self.status_label)
        
        layout.addWidget(music_frame)
    
    def play_music_a(self):
        """播放A段音樂"""
        if self.music_a_path:
            self.reset_button_styles()
            self.set_button_playing_style(self.play_a_button, "A")
            self.play_music(self.music_a_path, "A段音樂")
    
    def play_music_b(self):
        """播放B段音樂"""
        if self.music_b_path:
            self.reset_button_styles()
            self.set_button_playing_style(self.play_b_button, "B")
            self.play_music(self.music_b_path, "B段音樂")
    
    def set_button_playing_style(self, button, segment):
        """設置正在播放按鈕的樣式"""
        if segment == "A":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: 3px solid #f39c12;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            button.setText("🔊 正在播放 A 段")
        else:  # segment == "B"
            button.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    border: 3px solid #f39c12;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            button.setText("🔊 正在播放 B 段")
    
    def reset_button_styles(self):
        """重置按鈕樣式為默認狀態"""
        if hasattr(self, 'play_a_button'):
            self.play_a_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            self.play_a_button.setText("🎵 播放 A 段音樂")
        
        if hasattr(self, 'play_b_button'):
            self.play_b_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            self.play_b_button.setText("🎵 播放 B 段音樂")
    
    def play_music(self, music_path: str, label: str):
        """播放指定音樂"""
        try:
            p = Path(music_path).expanduser().resolve()
            if not p.exists():
                QMessageBox.warning(self, "音檔不存在", f"找不到{label}音檔：\n{p}")
                return
            
            self.player.setSource(QUrl.fromLocalFile(str(p)))
            self.player.play()
            self.status_label.setText(f"♪ 狀態：正在播放 {label}")
            self.status_label.setStyleSheet("""
                color: #27ae60; 
                background-color: #d5f4e6;
                border: 2px solid #27ae60;
                border-radius: 6px;
                padding: 8px;
                margin: 10px;
                font-weight: bold;
            """)
            
            print(f"[DEBUG] 播放{label}：{p}")
            
        except Exception as e:
            QMessageBox.critical(self, "播放錯誤", f"播放{label}時發生錯誤：\n{str(e)}")
    
    def stop_music(self):
        """停止音樂播放"""
        if self.player:
            self.player.stop()
        self.reset_button_styles()
        self.status_label.setText("♪ 狀態：已停止")
        self.status_label.setStyleSheet("""
            color: #e74c3c; 
            background-color: #fadbd8;
            border: 2px solid #e74c3c;
            border-radius: 6px;
            padding: 8px;
            margin: 10px;
            font-weight: bold;
        """)
    
    def show_current_question(self):
        """顯示當前問題 - 選項區域居中，選項文字左對齊"""
        # 清空選項
        for i in reversed(range(self.options_layout.count())):
            child = self.options_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        question = self.questions[self.current_index]
        self.question_label.setText(question["question"])
        
        # 創建選項容器 - 整體居中，內容左對齊
        options_container = QWidget()
        options_container.setFixedWidth(600)  # 固定寬度
        container_layout = QVBoxLayout(options_container)
        container_layout.setAlignment(Qt.AlignLeft)  # 選項內容左對齊
        container_layout.setSpacing(15)  # 選項間距
        container_layout.setContentsMargins(0, 10, 0, 10)
        
        # 創建選項
        self.button_group = QButtonGroup(self)
        for option in question["options"]:
            radio = QRadioButton(option)
            radio.setFont(QFont("Arial", 20))
            radio.setStyleSheet("""
                QRadioButton {
                    spacing: 12px;
                    padding: 10px;
                }
                QRadioButton::indicator {
                    width: 22px;
                    height: 22px;
                }
                QRadioButton::indicator:unchecked {
                    border: 2px solid #7f8c8d;
                    border-radius: 11px;
                    background-color: white;
                }
                QRadioButton::indicator:checked {
                    border: 2px solid #3498db;
                    border-radius: 11px;
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
        """上一題"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_question()
    
    def next_question(self):
        """下一題或完成"""
        # 檢查選擇
        selected = self.button_group.checkedButton()
        if not selected:
            QMessageBox.warning(self, "未選擇", "請選擇一個選項")
            return
        
        # 保存結果
        question = self.questions[self.current_index]
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
            self.stop_music()  # 完成前停止音樂
            self.reset_button_styles()  # 重置按鈕樣式
            self.next_callback(self.results)
    
    def closeEvent(self, event):
        """關閉事件處理"""
        self.stop_music()
        super().closeEvent(event)