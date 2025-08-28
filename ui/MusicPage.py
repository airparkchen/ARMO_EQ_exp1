# ui/MusicPage.py - 最小修改版本
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QHBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QFont

class MusicPage(QWidget):
    def __init__(self, music_path, next_page_callback, debug_mode=False):
        super().__init__()
        self.music_path = music_path
        self.next_page_callback = next_page_callback
        self.debug_mode = debug_mode  # 新增：除錯模式開關
        self.init_ui()
        self.init_music()

    def init_ui(self):
        # 主佈局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # 說明文字標籤
        instruction_text = "稍後會有音樂供您聆聽，待音樂播放完畢後頁面會自動跳轉，請好好放鬆～"
        if self.debug_mode:
            instruction_text += "\n\n[除錯模式] 您可以點擊下方按鈕跳過音樂"
            
        self.description_label = QLabel(instruction_text)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.description_label.setWordWrap(True)

        # 設定字體大小
        font = QFont()
        font.setPointSize(48)
        self.description_label.setFont(font)
        layout.addWidget(self.description_label, alignment=Qt.AlignCenter)

        # 新增：除錯模式跳過按鈕
        if self.debug_mode:
            button_layout = QHBoxLayout()
            button_layout.setAlignment(Qt.AlignCenter)
            
            self.skip_button = QPushButton("跳過音樂")
            self.skip_button.setFont(QFont("Arial", 24))
            self.skip_button.setFixedSize(200, 80)
            self.skip_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff6666;
                    color: white;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #ff4444;
                }
                QPushButton:pressed {
                    background-color: #ff2222;
                }
            """)
            self.skip_button.clicked.connect(self.skip_music)
            button_layout.addWidget(self.skip_button)
            
            layout.addLayout(button_layout)

        self.setLayout(layout)

    def skip_music(self):
        """跳過音樂播放"""
        if hasattr(self, 'player'):
            self.player.stop()
        self.next_page_callback()

    def init_music(self):
        # 初始化播放器
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)  # 設定音量至最大值
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(self.music_path))

        # 音樂播放結束時自動跳頁
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def showEvent(self, event):
        """當頁面顯示時開始播放音樂"""
        super().showEvent(event)
        self.start_music()

    def on_media_status_changed(self, status):
        # 音樂播放結束時自動執行換頁
        if status == QMediaPlayer.EndOfMedia:
            self.next_page_callback()

    def start_music(self):
        # 開始播放音樂
        self.player.play()